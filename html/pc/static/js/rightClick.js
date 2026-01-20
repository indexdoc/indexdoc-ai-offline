(function(global) {
    'use strict';

    var CustomContextMenu = {
        defaults: {
            menuId: 'custom-context-menu',
            menuClass: 'ccm-menu',
            itemClass: 'ccm-item',
            customItems: {} // { 'Label': function }
        },
        init: function(options) {
            this.opts = Object.assign({}, this.defaults, options);
            this._buildMenu();
            this._bindEvents();
        },
        _buildMenu: function() {
            // Remove existing
            var old = document.getElementById(this.opts.menuId);
            if (old) document.body.removeChild(old);

            // Create menu container
            var menu = document.createElement('div');
            menu.id = this.opts.menuId;
            menu.className = this.opts.menuClass;
            menu.style.position = 'absolute';
            menu.style.display = 'none';
            menu.style.background = '#fff';
            menu.style.border = '1px solid #ccc';
            menu.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
            menu.style.padding = '5px 0';
            menu.style.zIndex = 9999;
            menu.style.minWidth = '150px';
            menu.style.borderRadius = '4px';

            // Default items
            var items = [
                { label: '刷新', action: this._refresh.bind(this) },
                { label: '复制', action: this._copy.bind(this) },
                { label: '粘贴', action: this._paste.bind(this) }
            ];
            // Custom items
            for (var label in this.opts.customItems) {
                if (this.opts.customItems.hasOwnProperty(label)) {
                    items.push({ label: label, action: this.opts.customItems[label] });
                }
            }

            // Build items
            var self = this;
            items.forEach(function(item) {
                var div = document.createElement('div');
                div.className = self.opts.itemClass;
                div.style.padding = '8px 16px';
                div.style.cursor = 'pointer';
                div.style.whiteSpace = 'nowrap';
                div.textContent = item.label;
                div.addEventListener('click', function(e) {
                    e.stopPropagation();
                    self._hideMenu();
                    item.action();
                });
                div.addEventListener('mouseenter', function() {
                    this.style.backgroundColor = '#f0f0f0';
                });
                div.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = '';
                });
                menu.appendChild(div);
            });

            document.body.appendChild(menu);
            this.menu = menu;
        },
        _bindEvents: function() {
            var self = this;
            window.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                self._showMenu(e.pageX, e.pageY);
            });
            window.addEventListener('click', function() {
                self._hideMenu();
            });
            window.addEventListener('resize', function() {
                self._hideMenu();
            });
        },
        _showMenu: function(x, y) {
            var w = window.innerWidth;
            var h = window.innerHeight;
            var rect = this.menu.getBoundingClientRect();
            if (x + rect.width > w) x = w - rect.width - 5;
            if (y + rect.height > h) y = h - rect.height - 5;
            this.menu.style.left = x + 'px';
            this.menu.style.top = y + 'px';
            this.menu.style.display = 'block';
        },
        _hideMenu: function() {
            this.menu.style.display = 'none';
        },
        _refresh: function() {
            location.reload();
        },
        _copy: function() {
            var text = window.getSelection().toString();
            if (!text) return;
            navigator.clipboard.writeText(text).catch(function(err) {
                console.error('Copy failed', err);
            });
        },
        _paste: function() {
            var active = document.activeElement;
            if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) {
                navigator.clipboard.readText().then(function(text) {
                    if (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA') {
                        var start = active.selectionStart || 0;
                        var end = active.selectionEnd || 0;
                        var value = active.value;
                        active.value = value.slice(0, start) + text + value.slice(end);
                        active.setSelectionRange(start + text.length, start + text.length);
                    } else {
                        document.execCommand('insertText', false, text);
                    }
                }).catch(function(err) {
                    console.error('Paste failed', err);
                });
            }
        }
    };

    // Expose to global
    global.CustomContextMenu = CustomContextMenu;
})(this);