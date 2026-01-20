import time
import logging
import threading
from enum import Enum
from typing import Any, Optional, List

# 假设已有 duckdb_config
import numpy as np

from database.duckdb_config import duckdb_config
import duckdb


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    CANCELLED = "cancelled"


class SqlTask:
    def __init__(self, task_id: int, sql: str, params=None, is_many=False):
        self.task_id = task_id
        self.sql = sql
        self.params = params
        self.status = TaskStatus.PENDING
        self.result = None
        self.event = threading.Event()
        self.created_at = time.time()
        self.is_many = is_many


class DuckDBQueue:
    def __init__(self, default_timeout=30):
        self.tasks: List[SqlTask] = []  # 代替 queue.Queue
        self.is_running = False
        self.worker_thread = None
        self.task_id_counter = 0
        self.lock = threading.Lock()
        self.default_timeout = default_timeout
        self.conn = None  # 单连接

    def _get_next_id(self):
        with self.lock:
            self.task_id_counter += 1
            return self.task_id_counter

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.conn = duckdb.connect(database=duckdb_config['database'])
        self.conn.create_function('cosine_similarity', cosine_similarity,
                                  ['DOUBLE[]', 'DOUBLE[]'],
                                  'DOUBLE')
        self.worker_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.worker_thread.start()
        logging.info("DuckDB 队列启动")

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        with self.lock:
            for task in self.tasks:
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    task.event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=3)
        if self.conn:
            self.conn.close()
        logging.info("DuckDB 队列已停止")

    def submit_task(self, sql: str, params=None, timeout=None, is_many=False):
        task_id = self._get_next_id()
        task = SqlTask(task_id, sql, params, is_many)

        with self.lock:
            if not self.is_running:
                raise Exception("队列未运行")
            self.tasks.append(task)

        wait_timeout = timeout if timeout is not None else self.default_timeout
        finished = task.event.wait(timeout=wait_timeout)

        with self.lock:
            # 从列表中移除已完成或已取消的任务
            self.tasks = [t for t in self.tasks if t.task_id != task_id]

        if not finished:
            # 已经从 tasks 中移除，无需再 cancel
            raise TimeoutError(f"任务 {task_id} 排队/执行超时（>{wait_timeout}s）")

        if task.status == TaskStatus.CANCELLED:
            raise Exception(f"任务 {task_id} 已被取消")

        if task.result and not task.result['success']:
            raise Exception(task.result['error'])

        return task.result['data'] if task.result else None

    def _process_loop(self):
        while self.is_running:
            task = self._pop_next_task()
            if task is None:
                time.sleep(0.01)  # 避免忙等
                continue

            # 开始执行前再次检查是否已取消
            if task.status == TaskStatus.CANCELLED:
                continue

            task.status = TaskStatus.RUNNING
            self._execute_task(task)
            task.event.set()

    def _pop_next_task(self) -> Optional[SqlTask]:
        with self.lock:
            for i, task in enumerate(self.tasks):
                if task.status == TaskStatus.PENDING:
                    return self.tasks.pop(i)  # 移除并返回
            return None

    def _execute_task(self, task: SqlTask):
        try:
            if task.is_many:
                cursor = self.conn.executemany(task.sql, task.params)
            else:
                cursor = self.conn.execute(task.sql, task.params)
            upper_sql = task.sql.strip().upper()
            if (upper_sql.startswith("SELECT") or
                    upper_sql.startswith("PRAGMA") or
                    "RETURNING" in upper_sql):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                result_data = [dict(zip(columns, row)) for row in rows]
            else:
                result_data = None

            task.result = {
                'success': True,
                'data': result_data,
                'execution_time': time.time() - task.created_at
            }
            task.status = TaskStatus.DONE

        except Exception as e:
            logging.error(f"任务 {task.task_id} 执行失败: {str(e)}")
            task.result = {
                'success': False,
                'error': str(e),
                'data': None
            }
            task.status = TaskStatus.DONE

# 定义余弦相似度函数
def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    计算 a, b 两个向量的角度相似度（Angular Similarity）。
    返回值范围 [0.0, 1.0]，0 表示正交／无关，1 表示完全相同方向。
    """
    eps = 1e-8
    # 转成双精度 numpy 数组
    a_np = np.asarray(a, dtype=np.float64)
    b_np = np.asarray(b, dtype=np.float64)

    # 计算范数，防止为 0
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    if norm_a < eps or norm_b < eps:
        return 0.0

    # 计算原始余弦值，并 clamp 到 [-1, 1]
    cos_val = np.dot(a_np, b_np) / (norm_a * norm_b)
    cos_val = max(min(cos_val, 1.0), -1.0)

    # 转成角度相似度：angle = arccos(cos) ∈ [0, π], 再归一化
    angle = np.arccos(cos_val)
    sim = 1.0 - angle / np.pi

    return float(sim)