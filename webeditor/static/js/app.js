import {API} from './api.js';
import {Components} from './components.js';

/**
 * Essentials
 * astrbot_plugin_essentials
 *
 * 网页编辑器应用。
 *
 * @author 季楠
 * @since 2026/4/23 20:25
 */
export const App = {
    currentTab: 'users',
    currentUser: null,
    currentGroup: null,
    users: [],
    groups: [],
    searchQuery: '',

    elements: {},

    /**
     * 初始化。
     */
    init() {
        this.cacheElements();
        this.bindEvents();
        this.tryAutoLogin();
    },

    /**
     * 自动登录。
     */
    async tryAutoLogin() {
        const token = API.getToken();
        if (token) {
            try {
                const valid = await API.verifyToken(token);
                if (valid) {
                    this.hideLoginModal();
                    await this.loadData();
                    return;
                }
            } catch {
            }
            API.setToken(null);
        }
        this.showLoginModal();
    },

    /**
     * 显示登录界面。
     */
    showLoginModal() {
        document.getElementById('loginModal').classList.add('active');
        document.getElementById('tokenInput').value = '';
        document.getElementById('loginError').style.display = 'none';
        document.getElementById('app').style.display = 'none';
    },

    /**
     * 隐藏登录界面。
     */
    hideLoginModal() {
        document.getElementById('loginModal').classList.remove('active');
        document.getElementById('app').style.display = 'flex';
    },

    /**
     * 验证访问令牌。
     */
    async verifyToken() {
        const token = document.getElementById('tokenInput').value.trim();
        const loginError = document.getElementById('loginError');

        if (!token) {
            loginError.textContent = '请输入访问令牌。';
            loginError.style.display = 'block';
            return;
        }

        try {
            const valid = await API.verifyToken(token);
            if (valid) {
                this.hideLoginModal();
                await this.loadData();
            } else {
                loginError.textContent = '访问令牌无效。';
                loginError.style.display = 'block';
            }
        } catch (e) {
            loginError.textContent = e.message || '验证访问令牌失败。';
            loginError.style.display = 'block';
        }
    },

    /**
     * 缓存 DOM 元素。
     */
    cacheElements() {
        this.elements.userList = document.getElementById('userList');
        this.elements.userListItems = document.getElementById('userListItems');
        this.elements.groupList = document.getElementById('groupList');
        this.elements.groupListItems = document.getElementById('groupListItems');
        this.elements.searchInput = document.getElementById('searchInput');

        this.elements.userView = document.getElementById('userView');
        this.elements.groupView = document.getElementById('groupView');

        this.elements.userIdInput = document.getElementById('userIdInput');
        this.elements.userGroupsTags = document.getElementById('userGroupsTags');
        this.elements.userPermissionsBody = document.getElementById('userPermissionsBody');

        this.elements.groupNameInput = document.getElementById('groupNameInput');
        this.elements.groupDisplayInput = document.getElementById('groupDisplayInput');
        this.elements.groupWeightInput = document.getElementById('groupWeightInput');
        this.elements.groupParentsTags = document.getElementById('groupParentsTags');
        this.elements.groupPermissionsBody = document.getElementById('groupPermissionsBody');

        this.elements.addUserGroupSelect = document.getElementById('addUserGroupSelect');
        this.elements.addGroupParentSelect = document.getElementById('addGroupParentSelect');

        this.elements.permissionModal = document.getElementById('permissionModal');
        this.elements.addUserModal = document.getElementById('addUserModal');
        this.elements.addGroupModal = document.getElementById('addGroupModal');
    },

    /**
     * 绑定事件。
     */
    bindEvents() {
        document.getElementById('verifyTokenButton').addEventListener('click', () => this.verifyToken());
        document.getElementById('tokenInput').addEventListener('keypress', (event) => {
            if (event.key === 'Enter') this.verifyToken();
        });

        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => this.switchTab(button.dataset.tab));
        });

        this.elements.searchInput.addEventListener('input', (event) => {
            this.searchQuery = event.target.value.toLowerCase();
            this.renderCurrentList();
        });

        document.getElementById('addUserButton').addEventListener('click', () => this.showAddUserModal());
        document.getElementById('closeAddUserModal').addEventListener('click', () => this.hideAddUserModal());
        document.getElementById('cancelAddUserButton').addEventListener('click', () => this.hideAddUserModal());
        document.getElementById('confirmAddUserButton').addEventListener('click', () => this.createUser());
        document.getElementById('deleteUserButton').addEventListener('click', () => this.deleteUser());
        document.getElementById('addUserGroupButton').addEventListener('click', () => this.addUserToGroup());

        document.getElementById('addGroupButton').addEventListener('click', () => this.showAddGroupModal());
        document.getElementById('closeAddGroupModal').addEventListener('click', () => this.hideAddGroupModal());
        document.getElementById('cancelAddGroupButton').addEventListener('click', () => this.hideAddGroupModal());
        document.getElementById('confirmAddGroupButton').addEventListener('click', () => this.createGroup());
        document.getElementById('deleteGroupButton').addEventListener('click', () => this.deleteGroup());
        document.getElementById('saveGroupButton').addEventListener('click', () => this.saveGroup());
        document.getElementById('addGroupParentButton').addEventListener('click', () => this.addGroupParent());

        document.getElementById('closePermissionModal').addEventListener('click', () => this.hidePermissionModal());
        document.getElementById('cancelPermissionButton').addEventListener('click', () => this.hidePermissionModal());
        document.getElementById('confirmPermissionButton').addEventListener('click', () => this.confirmPermission());

        document.getElementById('addUserPermissionButton').addEventListener('click', () => this.showAddPermissionModal('user'));
        document.getElementById('addGroupPermissionButton').addEventListener('click', () => this.showAddPermissionModal('group'));

        document.getElementById('deleteSelectedPermissionsButton').addEventListener('click', () => this.deleteSelectedUserPermissions());
        document.getElementById('deleteSelectedGroupPermissionsButton').addEventListener('click', () => this.deleteSelectedGroupPermissions());

        document.getElementById('selectAllUserPermissions').addEventListener('change', (event) => {
            this.toggleSelectAll(event.target.checked, '.permission-checkbox');
            this.updateDeletePermissionsButton();
        });
        document.getElementById('selectAllGroupPermissions').addEventListener('change', (event) => {
            this.toggleSelectAll(event.target.checked, '.group-permission-checkbox');
            this.updateDeleteGroupPermissionsButton();
        });

        [this.elements.permissionModal, this.elements.addUserModal, this.elements.addGroupModal].forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.classList.remove('active');
            });
        });
    },

    /**
     * 加载数据。
     */
    async loadData() {
        try {
            await Promise.all([this.loadUsers(), this.loadGroups()]);
            this.renderCurrentList();
        } catch (e) {
            Components.showToast(`加载数据失败：${e.message}。`, 'error');
        }
    },

    /**
     * 加载用户列表。
     */
    async loadUsers() {
        try {
            this.users = await API.getUsers();
        } catch (e) {
            this.users = [];
            console.error('加载用户列表失败：', e);
        }
    },

    /**
     * 加载权限组列表。
     */
    async loadGroups() {
        try {
            this.groups = await API.getGroups();
        } catch (e) {
            this.groups = [];
            console.error('加载权限组列表失败：', e);
        }
    },

    /**
     * 切换标签页。
     */
    switchTab(tab) {
        this.currentTab = tab;

        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.toggle('active', button.dataset.tab === tab);
        });

        this.elements.userList.classList.toggle('hidden', tab !== 'users');
        this.elements.groupList.classList.toggle('hidden', tab !== 'groups');

        this.elements.userView.classList.add('hidden');
        this.elements.groupView.classList.add('hidden');

        this.currentUser = null;
        this.currentGroup = null;

        this.renderCurrentList();
    },

    /**
     * 渲染当前列表。
     */
    renderCurrentList() {
        if (this.currentTab === 'users') {
            this.renderUserList();
        } else {
            this.renderGroupList();
        }
    },

    /**
     * 渲染用户列表
     */
    renderUserList() {
        const container = this.elements.userListItems;
        container.innerHTML = '';

        const filtered = this.users.filter(user =>
            user.user_id.toLowerCase().includes(this.searchQuery)
        );

        if (filtered.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>暂无用户</p></div>';
            return;
        }

        filtered.forEach(user => {
            Components.renderUserItem(user, container, user.user_id === this.currentUser?.user_id);
        });
    },

    /**
     * 渲染权限组列表。
     */
    renderGroupList() {
        const container = this.elements.groupListItems;
        container.innerHTML = '';

        const filtered = this.groups.filter(group =>
            (group.name + (group.display || '')).toLowerCase().includes(this.searchQuery)
        );

        if (filtered.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>暂无权限组</p></div>';
            return;
        }

        filtered.forEach(group => {
            Components.renderGroupItem(group, container, group.name === this.currentGroup?.name);
        });
    },

    /**
     * 选择用户。
     */
    async selectUser(userId) {
        try {
            this.currentUser = await API.getUser(userId);
            this.currentGroup = null;

            this.elements.groupView.classList.add('hidden');
            this.elements.userView.classList.remove('hidden');

            this.renderUserView();
            this.renderCurrentList();
        } catch (e) {
            Components.showToast(`加载用户失败：${e.message}。`, 'error');
        }
    },

    /**
     * 渲染用户视图。
     */
    renderUserView() {
        const user = this.currentUser;
        this.elements.userIdInput.value = user.user_id;

        Components.renderUserGroupTags(
            this.elements.userGroupsTags,
            user.groups || [],
            user.user_id,
            user.groups || [],
            this.removeUserFromGroup.bind(this)
        );

        this.updateUserGroupSelect(user.groups || []);

        Components.clearTable(this.elements.userPermissionsBody);
        (user.permissions || []).forEach(permission => {
            Components.renderUserPermissionRow(permission, this.elements.userPermissionsBody, this.deleteUserPermission.bind(this));
        });

        this.elements.userPermissionsBody.querySelectorAll('.permission-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateDeletePermissionsButton());
        });
    },

    /**
     * 更新权限组选择框。
     */
    updateUserGroupSelect(currentGroups) {
        const select = this.elements.addUserGroupSelect;
        select.innerHTML = '<option value="">选择权限组</option>';

        this.groups.forEach(group => {
            if (!currentGroups.includes(group.name)) {
                const option = document.createElement('option');
                option.value = group.name;
                option.textContent = group.display || group.name;
                select.appendChild(option);
            }
        });
    },

    /**
     * 选择权限组。
     */
    async selectGroup(groupName) {
        try {
            this.currentGroup = await API.getGroup(groupName);
            this.currentUser = null;

            this.elements.userView.classList.add('hidden');
            this.elements.groupView.classList.remove('hidden');

            this.renderGroupView();
            this.renderCurrentList();
        } catch (e) {
            Components.showToast(`加载权限组失败：${e.message}。`, 'error');
        }
    },

    /**
     * 渲染权限组视图。
     */
    renderGroupView() {
        const group = this.currentGroup;

        this.elements.groupNameInput.value = group.name;
        this.elements.groupDisplayInput.value = group.display || '';
        this.elements.groupWeightInput.value = group.weight || 0;

        Components.renderGroupParentTags(
            this.elements.groupParentsTags,
            group.parents || [],
            group.name,
            this.removeGroupParent.bind(this)
        );

        this.updateGroupParentSelect(group.parents || []);

        Components.clearTable(this.elements.groupPermissionsBody);
        (group.permissions || []).forEach(permission => {
            Components.renderGroupPermissionRow(permission, this.elements.groupPermissionsBody, this.deleteGroupPermission.bind(this));
        });

        this.elements.groupPermissionsBody.querySelectorAll('.group-permission-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateDeleteGroupPermissionsButton());
        });
    },

    /**
     * 更新父权限组选择框。
     */
    updateGroupParentSelect(currentParents) {
        const select = this.elements.addGroupParentSelect;
        select.innerHTML = '<option value="">选择父权限组</option>';

        this.groups.forEach(group => {
            if (group.name !== this.currentGroup.name && !currentParents.includes(group.name)) {
                const option = document.createElement('option');
                option.value = group.name;
                option.textContent = group.display || group.name;
                select.appendChild(option);
            }
        });
    },

    showAddUserModal() {
        document.getElementById('newUserIdInput').value = '';
        this.elements.addUserModal.classList.add('active');
    },

    hideAddUserModal() {
        this.elements.addUserModal.classList.remove('active');
    },

    async createUser() {
        const userId = document.getElementById('newUserIdInput').value.trim();
        if (!userId) {
            Components.showToast('请输入用户 ID。', 'error');
            return;
        }

        try {
            await API.createUser(userId);
            Components.showToast('用户创建成功。');
            this.hideAddUserModal();
            await this.loadUsers();
            this.renderCurrentList();
            await this.selectUser(userId);
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async deleteUser() {
        if (!this.currentUser) return;

        if (!confirm(`确定要删除用户 ${this.currentUser.user_id} 吗？`)) return;

        try {
            await API.deleteUser(this.currentUser.user_id);
            Components.showToast('用户删除成功。');
            this.currentUser = null;
            this.elements.userView.classList.add('hidden');
            await this.loadUsers();
            this.renderCurrentList();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async addUserToGroup() {
        if (!this.currentUser) return;

        const groupName = this.elements.addUserGroupSelect.value;
        if (!groupName) {
            Components.showToast('请选择权限组。', 'error');
            return;
        }

        try {
            await API.addUserToGroup(this.currentUser.user_id, groupName);
            Components.showToast('新增用户权限组成功。');
            await this.selectUser(this.currentUser.user_id);
            await this.loadUsers();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async removeUserFromGroup(userId, groupName) {
        try {
            await API.removeUserFromGroup(userId, groupName);
            Components.showToast('移除用户权限组成功。');
            await this.selectUser(userId);
            await this.loadUsers();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    showAddPermissionModal(type) {
        this.permissionModalType = type;

        document.getElementById('permissionNodeInput').value = '';
        document.getElementById('permissionValueSelect').value = 'true';
        document.getElementById('permissionPriorityInput').value = '0';
        document.getElementById('permissionSourceInput').value = '';
        document.getElementById('permissionExpiryInput').value = '';
        document.getElementById('permissionSessionInput').value = '';
        document.getElementById('permissionModalTitle').textContent = '新增权限';
        this.elements.permissionModal.classList.add('active');
    },

    hidePermissionModal() {
        this.elements.permissionModal.classList.remove('active');
    },

    async confirmPermission() {
        const node = document.getElementById('permissionNodeInput').value.trim();
        const value = document.getElementById('permissionValueSelect').value === 'true';
        const priority = parseInt(document.getElementById('permissionPriorityInput').value, 10) || 0;
        const source = document.getElementById('permissionSourceInput').value.trim() || null;
        const expiryInput = document.getElementById('permissionExpiryInput').value;
        const expiry = expiryInput ? Math.floor(new Date(expiryInput).getTime() / 1000) : null;
        const session = document.getElementById('permissionSessionInput').value.trim() || null;

        if (!node) {
            Components.showToast('请输入权限。', 'error');
            return;
        }

        try {
            if (this.permissionModalType === 'user') {
                await API.addUserPermission(this.currentUser.user_id, {node, value, priority, source, expiry, session});
                Components.showToast('新增用户权限成功。');
                await this.selectUser(this.currentUser.user_id);
            } else {
                await API.addGroupPermission(this.currentGroup.name, {node, value, priority, source, expiry, session});
                Components.showToast('新增权限组权限成功。');
                await this.selectGroup(this.currentGroup.name);
            }
            this.hidePermissionModal();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async deleteUserPermission(node, session) {
        try {
            await API.deleteUserPermission(this.currentUser.user_id, node, session);
            Components.showToast('移除用户权限成功。');
            await this.selectUser(this.currentUser.user_id);
            await this.loadUsers();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async deleteGroupPermission(node, session) {
        try {
            await API.deleteGroupPermission(this.currentGroup.name, node, session);
            Components.showToast('移除权限组权限成功。');
            await this.selectGroup(this.currentGroup.name);
            await this.loadGroups();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    toggleSelectAll(checked, selector) {
        this.elements.userPermissionsBody.querySelectorAll(selector).forEach(checkbox => {
            checkbox.checked = checked
        });
    },

    updateDeletePermissionsButton() {
        const checked = this.elements.userPermissionsBody.querySelectorAll('.permission-checkbox:checked').length;
        document.getElementById('deleteSelectedPermissionsButton').disabled = checked === 0;
    },

    updateDeleteGroupPermissionsButton() {
        const checked = this.elements.groupPermissionsBody.querySelectorAll('.group-permission-checkbox:checked').length;
        document.getElementById('deleteSelectedGroupPermissionsButton').disabled = checked === 0;
    },

    async deleteSelectedUserPermissions() {
        const checkboxes = this.elements.userPermissionsBody.querySelectorAll('.permission-checkbox:checked');
        const permissions = Array.from(checkboxes).map(checkbox => ({
            node: checkbox.dataset.node,
            session: checkbox.dataset.session || null
        }));

        if (permissions.length === 0) return;

        try {
            await API.deleteUserPermissions(this.currentUser.user_id, permissions);
            Components.showToast(`已移除用户 ${permissions.length} 个权限。`);
            await this.selectUser(this.currentUser.user_id);
            await this.loadUsers();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async deleteSelectedGroupPermissions() {
        const checkboxes = this.elements.groupPermissionsBody.querySelectorAll('.group-permission-checkbox:checked');
        const permissions = Array.from(checkboxes).map(checkbox => ({
            node: checkbox.dataset.node,
            session: checkbox.dataset.session || null
        }));

        if (permissions.length === 0) return;

        try {
            await API.deleteGroupPermissions(this.currentGroup.name, permissions);
            Components.showToast(`已移除权限组 ${permissions.length} 个权限。`);
            await this.selectGroup(this.currentGroup.name);
            await this.loadGroups();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    showAddGroupModal() {
        document.getElementById('newGroupNameInput').value = '';
        document.getElementById('newGroupDisplayInput').value = '';
        this.elements.addGroupModal.classList.add('active');
    },

    hideAddGroupModal() {
        this.elements.addGroupModal.classList.remove('active');
    },

    async createGroup() {
        const name = document.getElementById('newGroupNameInput').value.trim();
        const display = document.getElementById('newGroupDisplayInput').value.trim();

        if (!name) {
            Components.showToast('请输入权限组编辑名。', 'error');
            return;
        }

        try {
            await API.createGroup({name, display, weight: 0, parents: [], permissions: []});
            Components.showToast('权限组创建成功。');
            this.hideAddGroupModal();
            await this.loadGroups();
            this.renderCurrentList();
            await this.selectGroup(name);
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async deleteGroup() {
        if (!this.currentGroup) return;

        if (!confirm(`确定要删除权限组 ${this.currentGroup.name} 吗？`)) return;

        try {
            await API.deleteGroup(this.currentGroup.name);
            Components.showToast('权限组删除成功。');
            this.currentGroup = null;
            this.elements.groupView.classList.add('hidden');
            await this.loadGroups();
            this.renderCurrentList();
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async saveGroup() {
        if (!this.currentGroup) return;

        const name = this.elements.groupNameInput.value.trim();
        const display = this.elements.groupDisplayInput.value.trim();
        const weight = parseInt(this.elements.groupWeightInput.value, 10) || 0;

        if (!name) {
            Components.showToast('权限组编辑名不能为空。', 'error');
            return;
        }

        try {
            await API.updateGroup(this.currentGroup.name, {
                name,
                display,
                weight,
                parents: this.currentGroup.parents || [],
                permissions: this.currentGroup.permissions || []
            });
            Components.showToast('权限组保存成功。');
            await this.loadGroups();
            if (name !== this.currentGroup.name) {
                await this.selectGroup(name);
            }
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async addGroupParent() {
        if (!this.currentGroup) return;

        const parentName = this.elements.addGroupParentSelect.value;
        if (!parentName) {
            Components.showToast('请选择父权限组。', 'error');
            return;
        }

        try {
            await API.addGroupParent(this.currentGroup.name, parentName);
            Components.showToast('添加父权限组成功。');
            await this.selectGroup(this.currentGroup.name);
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    },

    async removeGroupParent(groupName, parentName) {
        try {
            await API.removeGroupParent(groupName, parentName);
            Components.showToast('移除父权限组成功。');
            await this.selectGroup(groupName);
        } catch (e) {
            Components.showToast(e.message, 'error');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());