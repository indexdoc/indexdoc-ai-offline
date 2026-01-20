/**
 * combotree 模块组件,基于zTree封装的Layui模块.
 * 
 * MIT Licensed
 */
layui.extend({
  layztree: 'layztree/layztree'
}).define(['laytpl', 'layztree'], function(exports){
  "use strict";
  
  var $ = layui.$
  ,laytpl = layui.laytpl
  ,layztree = layui.layztree
  ,device = layui.device()
  ,clickOrMousedown = (device.mobile ? 'click' : 'mousedown')

  //模块名
  ,MOD_NAME = 'combotree'
  ,MOD_INDEX = 'layui_'+ MOD_NAME +'_index' //模块索引名

  //外部接口
  ,combotree = {
    config: {}
    ,index: layui[MOD_NAME] ? (layui[MOD_NAME].index + 10000) : 0

    //设置全局项
    ,set: function(options){
      var that = this;
      that.config = $.extend({}, that.config, options);
      return that;
    }
    
    //事件
    ,on: function(events, callback){
      return layui.onevent.call(this, MOD_NAME, events, callback);
    }
  }

  //操作当前实例
  ,thisModule = function(){
    var that = this
    ,options = that.config
    ,id = options.id || that.index;
    
    thisModule.that[id] = that; //记录当前实例对象
    
    return {
      config: options
      //重置实例
      ,reload: function(options){
        that.reload.call(that, options);
      }
    }
  }

  //字符常量
  ,STR_ELEM = 'layui-combotree', STR_HIDE = 'layui-hide', STR_DISABLED = 'layui-disabled', STR_NONE = 'layui-none'
  ,STR_ELEM_CONTENT = 'tree-content'
  
  //主模板
  ,TPL_MAIN = [
	'<div class = "layui-select-title" >',
	  '<input id="{{ d.data.elemId }}__names" type="text" value="" lay-verify="{{ d.data.layVerify }}" placeholder="{{ d.data.placeholder }}" class="layui-input" readonly>',
	  '<i class="layui-edge"></i>',
	  '<input hidden id="{{ d.data.elemId }}__index" value="{{ d.index }}">',
	'</div>',
	'<dl class="layui-anim layui-anim-upbit" style="max-height: {{ d.data.contentHight + 50 }}px;">',
	  '<div class="{{ d.elemContent }}" style="display: none;">',
	    '<input hidden id="{{ d.data.elemId }}__ids" name="{{ d.data.elemId }}">',
	    '<ul id="{{ d.data.elemId }}Tree" class="ztree" style="margin-top:0;"></ul>',
	  '</div>',
	'</dl>'
  ].join('')

  //构造器
  ,Class = function(options){
    var that = this;
    that.index = ++combotree.index;
    that.config = $.extend({}, that.config, combotree.config, options);
    that.render();
  };

  //默认配置
  //isMultiple 是否可以多选，多选时，显示checkbox，否则就是单选，显示radio
  //yChkboxType 当勾选时，联动方式("p"只影响父节点，"s"只影响子节点,"ps"父子节点都影响)，默认值ps
  //nChkboxType 当取消勾选时，联动方式("p"只影响父节点，"s"只影响子节点,"ps"父子节点都影响)，默认值ps
  //placeholder 提示
  //contentHight 下拉树展开时显示区域的显示高度，默认250px
  //expandAll 默认是否展开全部节点，默认值false
  //expandLevel 默认展开的级层，0表示根节点，默认值0
  //simpleData 指定数据格式是否使用简单数据格式，简单数据相关信息请参考zTree
  //data 树数据，根据simpleData的设置，确定是否使用简单数据格式
  //ajaxUrl 取得初期树数据url，如果设置了url就有限使用该url异步取得数据，不再使用data
  //ajaxParam ajax请求数据时，设置的请求参数
  //readonly 是否是只读对象
  //layVerify layui form验证申明
  //initValue combobox初期化值
  Class.prototype.config = {
    isMultiple: false,
	yChkboxType: 'ps',
	nChkboxType: 'ps',
	expandAll: false,
	expandLevel: 0,
	placeholder: "请选择",
	contentHight: 250,
	simpleData: true,
	ajaxUrl: "",
	ajaxParam: {},
	readonly: false,
	layVerify: "",
	initValue: "",
  };
  
  //重载实例
  Class.prototype.reload = function(options){
    var that = this;
    
    //防止数组深度合并
    layui.each(options, function(key, item){
      if(layui.type(item) === 'array') delete that.config[key];
    });
    
    that.config = $.extend(true, {}, that.config, options);
    that.render();
  };

  //渲染
  Class.prototype.render = function(){
    var that = this
    ,options = that.config;
    
	var othis = options.elem = $(options.elem);
    if(!othis[0]) return;
	// 每次只允许渲染一个对象，只支持id选择器
	if(othis.length != 1) return;
	options.elemId = othis.attr("id");
    // 初始化 id 属性 - 优先取 options > 元素 id > 自增索引
    options.id = 'id' in options ? options.id : (
      options.elem.attr('id') || that.index
    );

    combotree.thisId = options.id;

    // 若元素未设 lay-filter 属性，则取实例 id 值
    if(!options.elem.attr('lay-filter')){
      options.elem.attr('lay-filter', options.id);
    }

    //解析模板
    var thisElem = that.elem = $(laytpl(TPL_MAIN).render({
      data: options
	  ,elemContent: STR_ELEM_CONTENT
      ,index: that.index //索引
    }));
    
	othis.addClass("layui-form-select " + STR_ELEM);
	othis.append(thisElem);
	othis.find(".layui-select-title").bind("click", function () {
        if (options.readonly) {
            return;
        }
		if (!that.isSpread()) {
			// 非展开状态时，在展开前预先设置下拉树显示区域的尺寸和位置
			that.position();
		}
		// 切换展开状态
		thisModule.spread(othis);
	});
	
	// 初期化渲染zTree对象
    that.renderZtree();
	
	//阻止全局事件
    othis.find('.layui-anim').on('click mousedown', function(e){
      layui.stope(e);
    });
	
    that.events(); //事件
  };
  
  // 渲染zTree并放置在下拉区域内
  Class.prototype.renderZtree = function() {
    var that = this
    ,options = that.config;
    
    // 设置了ajaxUrl的话，优先通过该ajaxUrl取得数据
    if (options.ajaxUrl) {
        // 请求树的数据
        $.ajax({
            /* 请求的URL */
            url : options.ajaxUrl,
            /* 请求参数 */
            data : options.ajaxParam,
            /* 缓存 */
            cache : false,
            /* 请求类型 */
            type : "get",
            /* 数据类型 */
            dataType : "json",
            /* 成功处理 */
            success : function(result) {
                that.ztree = initZtree(result);
                // 设置初期化值
                if (options.initValue) {
                    that.setValue(options.initValue);
                }
            }
        });
    } else {
        that.ztree = initZtree(options.data);
        // 设置初期化值
        if (options.initValue) {
            that.setValue(options.initValue);
        }
    }
    
      // 加载ZTree
      function initZtree(data) {
        var othis = options.elem
        
        // zTree的初始设置
        var setting = {
            data: {
                simpleData: {
                    enable: options.simpleData ? true : false,
                    pIdKey: "pid"
                }
            },
            check: {
                chkboxType: { 
                    "Y": options.yChkboxType, 
                    "N": options.nChkboxType 
                },
                enable: true,
                chkStyle: options.isMultiple ? 'checkbox' : 'radio',
                radioType: "all",
            },
            view: {
                showIcon: false
            },
            callback: {
                onClick: onClick,
                onCheck: onCheck
            }
        };
        // 初期化渲染zTree对象
        var ztree = layztree.zTree.init($("#" + options.elemId + "Tree"), setting, data);
        // 是否展开所有节点
        if (options.expandAll) {
            ztree.expandAll(true);
        } else {
            ztree.expandAll(false);
            if (options.expandLevel > 0) {
                var expandLevel = options.expandLevel;
                // 获取需要展开的节点
                var expandNodes = ztree.getNodesByFilter(function(node) {
                    return node.level < expandLevel;
                }, false);
                // 展开节点
                for (var i in expandNodes) {
                    ztree.expandNode(expandNodes[i], true, false, true);
                }
            }
        }
        
        function onClick(event, treeId, treeNode) {
            // 执行 API click事件
            var filter = othis.attr('lay-filter');
            layui.event.call(event, MOD_NAME, 'click('+ filter +')', treeNode);
            // 勾选节点
            var zTree = layztree.zTree.getZTreeObj(treeId);
            zTree.checkNode(treeNode, !treeNode.checked, true, true);
            layui.stope(event);
        }
    
        function onCheck(event, treeId, treeNode) {
            var zTree = layztree.zTree.getZTreeObj(treeId);
            that.applySelectedNodes();
            if (zTree.setting.check.enable == true && zTree.setting.check.chkStyle == "radio") {
                thisModule.spread(othis);
            }
            layui.stope(event);
            // 执行 API check事件
            var filter = othis.attr('lay-filter');
            layui.event.call(event, MOD_NAME, 'check('+ filter +')', treeNode);
        }
        // 返回zTree对象        
        return ztree;
      }
  }

  // 设置树节点选择值
  Class.prototype.setValue = function(val) {
    var that = this
    ,options = that.config;
    // 值数组
    var valArray = [];
    // 如果是多选
    if (options.isMultiple) {
        // 通过逗号分割
        valArray = val.split(',');
    } else {
        valArray.push(val);
    }
    // 取消所有的选中
    that.uncheckAllNodes();
    // 遍历值
    for (var i = 0; i < valArray.length; i++) {
        // 查找文本
        var node = that.ztree.getNodeByParam("id", valArray[i]);
        // 如果找到，则选中
        if (node != null) {
            that.ztree.checkNode(node, true, true);
        }
    }
    // 应用选中这些节点
    that.applySelectedNodes();
  }

  // 取得选择树节点的值，多个节点被选择时，节点的值以逗号分割
  Class.prototype.getValue = function() {
    var that = this;
    // 获得所有被选中的节点
    var nodeArray = that.ztree.getCheckedNodes(true) || [];
    var values = [];
    for (var i = 0; i < nodeArray.length; i++) {
      values.push(nodeArray[i].id);
    }
    return values.join(',');
  }
  
  Class.prototype.uncheckAllNodes = function() {
    var that = this;
    // 获得所有被选中的节点
    var nodeArray = that.ztree.getCheckedNodes(true) || [];
    // 选中对象
    for (var i = 0; i < nodeArray.length; i++) {
        // 选中对象
        that.ztree.checkNode(nodeArray[i], false);
    }
  }

  // 将选中的节点应用到文本和值域中
  Class.prototype.applySelectedNodes = function() {
    var that = this
    ,options = that.config;
    // 获得所有被选中的节点
    var nodes = that.ztree.getCheckedNodes(true) || [];
    var names = [];
    var ids = [];
    for (var i = 0, l = nodes.length; i < l; i++) {
        names.push(nodes[i].name);
        ids.push(nodes[i].id);
    }
    $("#" + options.elemId + "__names").attr("value", names.join(','));
    $("#" + options.elemId + "__names").attr("title", names.join(','));
    $("#" + options.elemId + "__ids").attr("value", ids.join(','));
  }

  // 判断下拉树展开状态
  Class.prototype.isSpread = function() {
    var that = this
    ,options = that.config
	,othis = options.elem;
	return othis.hasClass("layui-form-selected");	
  }
  
  // 设置下拉树的尺寸和位置
  Class.prototype.position = function() {
    var that = this
    ,options = that.config
	,othis = options.elem;
	othis.find("." + STR_ELEM_CONTENT).css({
		left: othis.offset().left + "px",
		top: othis.offset().top + othis.height() + "px",
		height: options.contentHight + "px",
		width: othis.width() - 19
	});
  }
  
  //事件
  Class.prototype.events = function(){
    var that = this
    ,options = that.config;
    var CLASS = 'layui-form-select', TITLE = 'layui-select-title';
    var hide = function(e, clear){
      if(!$(e.target).parent().hasClass(TITLE) || clear){
        $('.'+CLASS).removeClass(CLASS+'ed ' + CLASS+'up');
      }
    };
    $(document).off('click', hide).on('click', hide); // 点击其它元素关闭 select
  };
  
  //全局事件
  ;!function(){
    var _WIN = $(window)
    ,_DOC = $(document);
    
    //自适应定位
    _WIN.on('resize', function(){
      if(!combotree.thisId) return;
      var that = thisModule.getThis(combotree.thisId);
      if(!that) return;
      
      if(!$('.'+ STR_ELEM)[0]){
        return false;
      }
      
      var options = that.config;
      
      if(options.trigger === 'contextmenu'){
        that.remove();
      } else {
        that.position();
      }
    });
    
  }();
  
  //记录所有实例
  thisModule.that = {}; //记录所有实例对象
  
  // 展开或折叠下拉框
  thisModule.spread = function(othis) {
	var isSpread = othis.hasClass("layui-form-selected");
	if (isSpread) {
		othis.removeClass("layui-form-selected");
		othis.find("." + STR_ELEM_CONTENT).fadeOut("fast");
	} else {
		othis.addClass("layui-form-selected");
		othis.find("." + STR_ELEM_CONTENT).slideDown("fast");
	}
  }
  
  //获取当前实例对象
  thisModule.getThis = function(id){
    var that = thisModule.that[id];
    if(!that) hint.error(id ? (MOD_NAME +' instance with ID \''+ id +'\' not found') : 'ID argument required');
    return that || null;
  };
  
  /** 对外开放接口 **/
  // 设置comboztree的值
  combotree.setValue = function(id, val) {
    var that = thisModule.getThis(id);
    if (that) {
      that.setValue(val);
    }
  }

  // 取得下拉树当前选中的值，多个节点被选中时，值以逗号分割
  combotree.getValue = function(id) {
    var that = thisModule.getThis(id);
    return that ? that.getValue() : null;
  }
  
  //重载实例
  combotree.reload = function(id, options){
    var that = thisModule.that[id];
    that.reload(options);

    return thisModule.call(that);
  };

  //核心入口
  combotree.render = function(options){
    var inst = new Class(options);	
    return thisModule.call(inst);
  };

  exports(MOD_NAME, combotree);
});
