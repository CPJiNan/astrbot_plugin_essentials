import {App} from "./app";

/**
 * Essentials
 * astrbot_plugin_essentials
 *
 * 网页编辑器组件。
 *
 * @author 季楠
 * @since 2026/4/23 20:45
 */
export const Components = {
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
            if (dataAttr) button.dataset[dataAttr] = dataValue;
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

    _renderPermissionRow(permission, tbody, onDelete, columns) {
        const tr = document.createElement('tr');
        tr.dataset.node = permission.node;
        tr.innerHTML = columns;
        tr.querySelector('button').addEventListener('click', () => onDelete(permission.node, permission.session));
        tbody.appendChild(tr);
    },

    renderUserPermissionRow(permission, tbody, onDelete) {
        this._renderPermissionRow(
            permission,
            tbody,
            onDelete,
            `
                <td><input type="checkbox" class="permission-checkbox" data-node="${this.escapeHtml(permission.node)}" data-session="${this.escapeHtml(permission.session || '')}"></td>
                <td>${this.escapeHtml(permission.node)}</td>
                <td class="${permission.value ? 'permission-value-true' : 'permission-value-false'}">${permission.value ? 'true' : 'false'}</td>
                <td>${permission.priority || 0}</td>
                <td>${permission.source || '-'}</td>
                <td>${permission.expiry ? this.formatDate(permission.expiry) : '-'}</td>
                <td>${permission.session || '-'}</td>
                <td>
                    <button class="button button-danger button-small" data-node="${this.escapeHtml(permission.node)}" data-session="${this.escapeHtml(permission.session || '')}">删除</button>
                </td>
            `
        );
    },

    renderGroupPermissionRow(permission, tbody, onDelete) {
        this._renderPermissionRow(
            permission,
            tbody,
            onDelete,
            `
                <td><input type="checkbox" class="group-permission-checkbox" data-node="${this.escapeHtml(permission.node)}" data-session="${this.escapeHtml(permission.session || '')}"></td>
                <td>${this.escapeHtml(permission.node)}</td>
                <td class="${permission.value ? 'permission-value-true' : 'permission-value-false'}">${permission.value ? 'true' : 'false'}</td>
                <td>${permission.priority || 0}</td>
                <td>${permission.source || '-'}</td>
                <td>${permission.expiry ? this.formatDate(permission.expiry) : '-'}</td>
                <td>${permission.session || '-'}</td>
                <td>
                    <button class="button button-danger button-small" data-node="${this.escapeHtml(permission.node)}" data-session="${this.escapeHtml(permission.session || '')}">删除</button>
                </td>
            `
        );
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    formatDate(timestamp) {
        try {
            const date = new Date(timestamp * 1000);
            return date.toLocaleString('zh-CN');
        } catch {
            return timestamp;
        }
    },
};