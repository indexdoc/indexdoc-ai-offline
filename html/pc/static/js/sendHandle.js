var button = document.getElementById("sendBtn");
var stop = document.getElementById("stop");
var source;
var chatFlag = true;
var task_id = '';
var currentCount = '';
var talkStatus = 'true';
var timeoutId = '';
var sendFlag = true;
var getFlag = true;
var userInput = '';
var markdownBuffer = '';
var lastRenderedContent = '';




//获取列队
function taskRank() {
  // 获取用户输入的文本
  var _userInput = document.getElementById("userInput").value;
  if (_userInput != '') {
    userInput = _userInput;
  }
  if (userInput != '') {
    var userName = sessionStorage.getItem('userName');
    $.ajax({
      url: '/api/lcapi/task?task_id=' + task_id + '&name=' + userName,
      type: 'get',
      contentType: false,
      processData: false,
      success: function (res) {
        // console.log(res);
        console.log('状态：' + res.obj.status, '排队人数：' + res.obj.length);
        task_id = res.obj.task_id;
        currentCount = res.obj.length;
        talkStatus = res.obj.status;
        sendMessage();
      },
      error: function (error) {
        console.error(error);
      }
    });
  } else {
    layer.msg('请输入问题');
  }
}


function checkTaskRank() {
  if (talkStatus == 'false') {
    taskRank();
  } else if (talkStatus == 'true') {
    console.log('清除定时器');
    clearTimeout(timeoutId);
  }
}


//发送消息
function sendMessage() {
  if (sendFlag) {
    if (userInput.trim() !== "") {
      // 创建新的聊天消息元素
      var chatMessages = document.getElementById("chatMessages");
      var messageContainer = document.createElement("div");
      messageContainer.className = "message user-message";
      var messageImg = document.createElement("div");
      messageImg.className = "messageImg";
      messageContainer.appendChild(messageImg);
      // 添加用户头像
      var userAvatar = "<img src='/admin/static/img/people.png' alt='User Avatar' class='avatar'/>";
      messageImg.innerHTML = userAvatar;
      // 添加用户消息内容
      var messageContent = document.createElement("div");
      messageContent.className = "message-content";
      messageContent.textContent = userInput;
      // 将头像和消息内容添加到消息元素中
      messageContainer.appendChild(messageContent);
      // 将消息元素添加到聊天容器中
      chatMessages.appendChild(messageContainer);
      // 清空输入框
      document.getElementById("userInput").value = "";
    }
  } else {
    // layer.msg('排队中，请等候');
  }
  //连接
  connectSSE(userInput);
}

function handleKeyDown(event) {
  if (event.key === 'Enter') {
    if (chatFlag) {
      event.preventDefault();
      if (button.style.display == 'block') {
        taskRank();
      }
    }
  }
}

//
function stopMessage() {
  button.style.display = "block";
  stop.style.display = "none";
  source.close();
  $.ajax({
    url: '/api/lcapi/stop_task?task_id=' + task_id,
    type: 'get',
    contentType: false,
    processData: false,
    success: function (res) {
      // console.log(res);
      task_id = '';
      currentCount = '';
      talkStatus = '';
      chatFlag = true;
      sendFlag = true;
      getFlag = true;
      taskRankFlag = false;
      markdownBuffer = '';
      lastRenderedContent = '';
      addOperateBtn();
    },
    error: function (error) {
      console.error(error);
    }
  });
}

//sse连接
function connectSSE(data) {
  if (talkStatus == 'true') {
    //移除重新生成按钮
    var div = document.getElementById(_refreshId);
    if (div) {
      div.parentNode.removeChild(div);
    }
    button.style.display = "none";
    stop.style.display = "flex";
    chatFlag = false;
    getMessage();
    const dmp = new diff_match_patch();
    var prompt = 'default';
    source = new EventSource('/api/lcapi/aichat?msg=' + data + '&conversation_id=' + conversation_id + '&task_id=' + task_id + '&prompt=' + prompt);
    // source = new EventSource('https://www.aituple.com/api/ck/data?msg=' + data + '&conversation_id=' + conversation_id + '&task_id=' + task_id);
    // source = new EventSource('http://192.168.232.222:5000/ck/data?msg=' + data + '&conversation_id=' + conversation_id);
    // source = new EventSource('https://www.aituple.com/api/ck/data?msg=' + data + '&chat_type=kb_chat' + '&knowledge_base_name=法律');
    document.getElementById(_messageContentID).innerHTML = '';

    source.onmessage = function (e) {
      console.log(e.data);
      var msg = JSON.parse(e.data);
      if (msg.type == 'data') {
        // append(msg.data);
        const chunk = msg.data;
        /*
        1.接收实时数据块并累积到 markdownBuffer 中。
        2.将累积的 Markdown 数据解析为 HTML。
        3.计算新旧内容的差异并生成补丁。
        4.应用补丁并更新页面内容，只更新变化的部分，而不是整个内容。
        */
        markdownBuffer += chunk;

        const newContent = marked.parse(markdownBuffer);
        // 计算差异
        const diffs = dmp.diff_main(lastRenderedContent, newContent);
        dmp.diff_cleanupSemantic(diffs);

        const patches = dmp.patch_make(lastRenderedContent, newContent, diffs);
        const results = dmp.patch_apply(patches, lastRenderedContent);

        if (results[0]) {
          lastRenderedContent = newContent;
          document.getElementById(_messageContentID).innerHTML = lastRenderedContent;
        }
        var contentContainer = document.getElementById('chatMessages');
        contentContainer.scrollTop = contentContainer.scrollHeight;
      } else {

      }
    };
    source.onopen = function (e) {
      console.log("Connecting server!");
    };
    source.onerror = function (e) {
      console.log("error");
      console.log(e);
      button.style.display = "block";
      stop.style.display = "none";
      // markdownConvert();
      task_id = '';
      currentCount = '';
      talkStatus = '';
      source.close();
      chatFlag = true;
      sendFlag = true;
      getFlag = true;
      taskRankFlag = false;
      markdownBuffer = '';
      lastRenderedContent = '';
      addOperateBtn();
    };
    //增加自定义事件sendMessage的监听
    source.addEventListener("message", function (e) {
      // console.log(e);
    })
  } else if (talkStatus == 'false') {
    //加载中，显示排队人数
    timeoutId = setTimeout(checkTaskRank, 3000);
    getMessage();
    sendFlag = false;
    getFlag = false;
    document.getElementById(_messageContentID).innerHTML = '';
    append('排队中，当前排队人数：' + currentCount + '人');
    button.style.display = "none";
  } else if (talkStatus == 'delete') {
    //列队失效，重新排队
    task_id = '';
    currentCount = '';
    talkStatus = '';
    taskRank();
  }
}

function addOperateBtn() {
  //添加复制,重新生成按钮
  var operatBtn = document.createElement("div");
  operatBtn.className = "operatBtn";
  _operatBtnId = "operatBtn_ " + generateUniqueId();
  operatBtn.setAttribute("id", _operatBtnId);
  _operatBtnID = _operatBtnId;
  document.getElementById(_messageContentID).appendChild(operatBtn);
  // 创建复制
  var img1 = document.createElement("img");
  img1.src = "/admin/static/img/copy.png";
  img1.className = "copyImg";
  var tooltip1 = document.createElement("div");
  tooltip1.className = "tooltip-container";
  tooltip1.id = "copy";
  tooltip1.setAttribute('data-tip', '复制');
  tooltip1.setAttribute('data-id', _messageContentID);
  tooltip1.setAttribute('onclick', 'copy("' + _messageContentID + '")');
  tooltip1.appendChild(img1);
  // 创建刷新
  _refreshId = generateUniqueId();
  var img2 = document.createElement("img");
  img2.src = "/admin/static/img/refresh.png";
  img2.className = "copyImg";
  var tooltip2 = document.createElement("div");
  tooltip2.className = "tooltip-container";
  tooltip2.id = _refreshId;
  tooltip2.setAttribute('data-tip', '重新生成');
  tooltip2.appendChild(img2);
  tooltip2.setAttribute('onclick', 'regenerate()');
  document.getElementById(_operatBtnId).appendChild(tooltip1);
  document.getElementById(_operatBtnId).appendChild(tooltip2);
}


function copy(_messageContentID) {
  console.log(_messageContentID);
  var div = document.getElementById(_messageContentID);
  const combinedText = getAllText(div);
  const textArea = document.createElement("textarea");
  textArea.value = combinedText;
  document.body.appendChild(textArea);
  textArea.select();
  try {
    document.execCommand('copy');
    // alert('Text copied to clipboard');
  } catch (err) {
    console.log('Failed to copy text');
  }
  document.body.removeChild(textArea);
}

function getAllText(element) {
  let text = '';
  element.childNodes.forEach(node => {
    if (node.nodeType === Node.TEXT_NODE) {
      text += node.textContent.trim() + ' ';
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      text += ' ' + getAllText(node);
    }
  });
  return text.trim();
}

function regenerate() {
  taskRank();
}

function append(message) {
  var id = document.getElementById(_messageContentID);
  // var currentCherry = new Cherry(Object.assign({}, cherryConfig, {
  //   el: id
  // }));
  // currentCherry.setMarkdown(message);
  // id.append(currentCherry);
  var html = marked.parse(message);
  id.innerHTML += html;
}

function markdownConvert() {
  var message = document.getElementById(_messageContentID).innerHTML;
  var html = marked.parse(message);
  message = html;
}

function escapeHtml(html) {
  let text = document.createTextNode(html);
  let div = document.createElement('div');
  div.appendChild(text);
  return div.innerHTML;
}

//接收消息显示
function getMessage() {
  if (getFlag) {
    var chatMessages = document.getElementById("chatMessages");
    var messageContainer = document.createElement("div");
    messageContainer.className = "message";
    var messageImg = document.createElement("div");
    messageImg.className = "messageImg";
    messageContainer.appendChild(messageImg);
    var userAvatar = "<img src='/admin/static/img/logo.png' alt='User Avatar' class='avatar'/>";
    messageImg.innerHTML = userAvatar;

    // 添加用户消息内容
    var messageContent = document.createElement("div");
    messageContent.className = "message-content";
    _id = "messageContent_ " + generateUniqueId();
    messageContent.setAttribute("id", _id);
    _messageContentID = _id;

    //添加复制,重新生成按钮
    var operatBtn = document.createElement("div");
    operatBtn.className = "operatBtn";
    _operatBtnId = "operatBtn_ " + generateUniqueId();
    operatBtn.setAttribute("id", _operatBtnId);
    _operatBtnID = _operatBtnId;

    // 将头像和消息内容添加到消息元素中
    messageContainer.appendChild(messageContent);

    // 将消息元素添加到聊天容器中
    chatMessages.appendChild(messageContainer);
  } else {
    // layer.msg('排队中，请等候');
  }
}

function generateUniqueId() {
  // 生成唯一 ID 的逻辑，可以使用库或其他方法
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = Math.random() * 16 | 0,
      v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}