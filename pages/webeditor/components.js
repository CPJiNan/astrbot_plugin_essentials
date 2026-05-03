/**
 * Essentials
 * astrbot_plugin_essentials
 *
 * 网页编辑器组件。
 *
 * @author 季楠
 * @since 2026/4/23 20:45
 */
const Components = {
    _renderListItem(type, id, name, isActive) {
        const div = document.createElement('div');
        div.className = `list-item${isActive ? ' active' : ''}`;
        div.dataset[type === 'user' ? 'userId' : 'groupName'] = id;
        const nameSpan = document.createElement('span');
        nameSpan.className = 'list-item-name';
        nameSpan.textContent = name;
        div.appendChild(nameSpan);
        return div;
    },

    renderUserItem(user, container, isActive = false) {
        const div = this._renderListItem('user', user.user_id, user.user_id, isActive);
        if (user.permissions?.length > 0) {
            const badge = document.createElement('span');
            badge.className = 'list-item-badge';
            badge.textContent = String(user.permissions.length);
            div.appendChild(badge);
        }
        div.addEventListener('click', () => App.selectUser(user.user_id));
        container.appendChild(div);
    },

    renderGroupItem(group, container, isActive = false) {
        const div = this._renderListItem('group', group.name, group.display || group.name, isActive);
        div.addEventListener('click', () => App.selectGroup(group.name));
        container.appendChild(div);
    },

    _renderTags(container, items, getTagContent, onRemove) {
        container.innerHTML = '';
        if (!items?.length) return;
        items.forEach(item => {
            const tag = document.createElement('span');
            tag.className = 'group-tag';
            const {text, dataAttr, dataValue} = getTagContent(item);
            tag.textContent = text;
            const button = document.createElement('button');
            button.className = 'remove-tag';
            button.textContent = '×';
            switch (dataAttr) {
                case 'group':
                    button.dataset.group = dataValue;
                    break;
                case 'parent':
                    button.dataset.parent = dataValue;
                    break;
            }
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                onRemove(item);
            });
            tag.appendChild(button);
            container.appendChild(tag);
        });
    },

    renderUserGroupTags(container, groups, userId, onRemove) {
        this._renderTags(
            container,
            groups,
            groupName => ({text: groupName, dataAttr: 'group', dataValue: groupName}),
            groupName => onRemove(userId, groupName)
        );
    },

    renderGroupParentTags(container, parents, groupName, onRemove) {
        this._renderTags(
            container,
            parents,
            parentName => ({text: parentName, dataAttr: 'parent', dataValue: parentName}),
            parentName => onRemove(groupName, parentName)
        );
    },

    _renderPermissionRow(permission, tbody, onDelete, type = 'user') {
        const tr = document.createElement('tr');
        tr.dataset.node = permission.node;

        const tdCheckbox = document.createElement('td');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = type === 'user' ? 'user-permission-checkbox' : 'group-permission-checkbox';
        checkbox.dataset.node = permission.node;
        checkbox.dataset.session = permission.session || '';
        tdCheckbox.appendChild(checkbox);
        tr.appendChild(tdCheckbox);

        const tdNode = document.createElement('td');
        tdNode.textContent = permission.node;
        tr.appendChild(tdNode);

        const tdValue = document.createElement('td');
        tdValue.className = permission.value ? 'permission-value-true' : 'permission-value-false';
        tdValue.textContent = permission.value ? 'true' : 'false';
        tr.appendChild(tdValue);

        const tdPriority = document.createElement('td');
        tdPriority.textContent = permission.priority || 0;
        tr.appendChild(tdPriority);

        const tdSource = document.createElement('td');
        tdSource.textContent = permission.source || '-';
        tr.appendChild(tdSource);

        const tdExpiry = document.createElement('td');
        tdExpiry.textContent = permission.expiry ? this.formatDate(permission.expiry) : '-';
        tr.appendChild(tdExpiry);

        const tdSession = document.createElement('td');
        tdSession.textContent = permission.session || '-';
        tr.appendChild(tdSession);

        const tdAction = document.createElement('td');
        const button = document.createElement('button');
        button.className = 'button button-danger button-small';
        button.dataset.node = permission.node;
        button.dataset.session = permission.session || '';
        button.textContent = '删除';
        button.addEventListener('click', () => onDelete(permission.node, permission.session));
        tdAction.appendChild(button);
        tr.appendChild(tdAction);

        tbody.appendChild(tr);
    },

    renderUserPermissionRow(permission, tbody, onDelete) {
        this._renderPermissionRow(permission, tbody, onDelete, 'user');
    },

    renderGroupPermissionRow(permission, tbody, onDelete) {
        this._renderPermissionRow(permission, tbody, onDelete, 'group');
    },

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        requestAnimationFrame(() => {
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                toast.addEventListener('transitionend', () => toast.remove(), {once: true});
            }, 3000);
        });
    },

    formatDate(timestamp) {
        try {
            const date = new Date(timestamp * 1000);
            return date.toLocaleString('zh-CN');
        } catch {
            return timestamp;
        }
    }
};