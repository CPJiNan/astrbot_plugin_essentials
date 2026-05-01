/**
 * Essentials
 * astrbot_plugin_essentials
 *
 * 网页编辑器 HTTP 接口。
 *
 * @author 季楠
 * @since 2026/4/22 21:35
 */
const API = {
    baseUrl: '/api',
    _token: null,

    /**
     * 发送 HTTP 请求。
     */
    async _fetch(url, options) {
        if (url.startsWith(this.baseUrl)) {
            return fetch(url, options);
        } else throw new Error(`请求的 URL 不在白名单内：${url}。`);
    },

    /**
     * 设置访问令牌。
     */
    setToken(token) {
        this._token = token;
        if (token) {
            sessionStorage.setItem('auth_token', token);
        } else {
            sessionStorage.removeItem('auth_token');
        }
    },

    /**
     * 获取访问令牌。
     */
    getToken() {
        if (!this._token) {
            this._token = sessionStorage.getItem('auth_token');
        }
        return this._token;
    },

    /**
     * 构建带有访问令牌的请求头。
     */
    _authHeaders(extra = {}) {
        const headers = {...extra};
        const token = this.getToken();
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
        return headers;
    },

    /**
     * 验证访问令牌。
     */
    async verifyToken(token) {
        const response = await this._fetch(`${this.baseUrl}/auth/verify`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token})
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.error || `验证访问令牌失败：${response.status}。`);
        }
        const data = await response.json();
        if (data.valid) {
            this.setToken(token);
        }
        return data.valid;
    },

    /**
     * 获取用户。
     */
    async getUser(userId) {
        const response = await this._fetch(`${this.baseUrl}/users/${encodeURIComponent(userId)}`, {
            headers: this._authHeaders()
        });
        if (!response.ok) throw new Error(`获取用户失败：${response.status}。`);
        return response.json();
    },

    /**
     * 获取用户列表。
     */
    async getUsers() {
        const response = await this._fetch(`${this.baseUrl}/users`, {
            headers: this._authHeaders()
        });
        if (!response.ok) throw new Error(`获取用户列表失败：${response.status}。`);
        return response.json();
    },

    /**
     * 创建用户。
     */
    async createUser(userId) {
        const response = await this._fetch(`${this.baseUrl}/users`, {
            method: 'POST',
            headers: this._authHeaders({'Content-Type': 'application/json'}),
            body: JSON.stringify({user_id: userId})
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `创建用户失败：${response.status}。`);
        }
        return response.json();
    },

    /**
     * 删除用户。
     */
    async deleteUser(userId) {
        const response = await this._fetch(`${this.baseUrl}/users/${encodeURIComponent(userId)}`, {
            method: 'DELETE',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `删除用户失败：${response.status}。`);
        }
    },

    /**
     * 获取权限组。
     */
    async getGroup(groupName) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}`, {
            headers: this._authHeaders()
        });
        if (!response.ok) throw new Error(`获取权限组失败：${response.status}。`);
        return response.json();
    },

    /**
     * 获取权限组列表。
     */
    async getGroups() {
        const response = await this._fetch(`${this.baseUrl}/groups`, {
            headers: this._authHeaders()
        });
        if (!response.ok) throw new Error(`获取权限组列表失败：${response.status}。`);
        return response.json();
    },

    /**
     * 创建权限组。
     */
    async createGroup(group) {
        const response = await this._fetch(`${this.baseUrl}/groups`, {
            method: 'POST',
            headers: this._authHeaders({'Content-Type': 'application/json'}),
            body: JSON.stringify(group)
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `创建权限组失败：${response.status}。`);
        }
        return response.json();
    },

    /**
     * 删除权限组。
     */
    async deleteGroup(groupName) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}`, {
            method: 'DELETE',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `删除权限组失败：${response.status}。`);
        }
    },

    /**
     * 更新权限组。
     */
    async updateGroup(groupName, group) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}`, {
            method: 'PUT',
            headers: this._authHeaders({'Content-Type': 'application/json'}),
            body: JSON.stringify(group)
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `更新权限组失败：${response.status}。`);
        }
        return response.json();
    },

    /**
     * 获取用户权限列表。
     */
    async getUserPermissions(userId) {
        const response = await this._fetch(`${this.baseUrl}/users/${encodeURIComponent(userId)}/permissions`, {
            headers: this._authHeaders()
        });
        if (!response.ok) throw new Error(`获取用户权限列表失败：${response.status}。`);
        return response.json();
    },

    /**
     * 新增用户权限。
     */
    async addUserPermission(userId, permission) {
        const response = await this._fetch(`${this.baseUrl}/users/${encodeURIComponent(userId)}/permissions`, {
            method: 'POST',
            headers: this._authHeaders({'Content-Type': 'application/json'}),
            body: JSON.stringify(permission)
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `新增用户权限失败：${response.status}。`);
        }
        return response.json();
    },

    /**
     * 移除用户权限。
     */
    async deleteUserPermission(userId, node, session) {
        let url = `${this.baseUrl}/users/${encodeURIComponent(userId)}/permissions/${encodeURIComponent(node)}`;
        if (session) {
            url += `?session=${encodeURIComponent(session)}`;
        }
        const response = await this._fetch(url, {
            method: 'DELETE',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `移除用户权限失败：${response.status}。`);
        }
    },

    /**
     * 批量移除用户权限。
     */
    async deleteUserPermissions(userId, nodes) {
        const results = [];
        for (const {node, session} of nodes) {
            try {
                await this.deleteUserPermission(userId, node, session);
            } catch (e) {
                results.push({node, error: e.message});
            }
        }
        return results;
    },

    /**
     * 获取权限组权限列表。
     */
    async getGroupPermissions(groupName) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}/permissions`, {
            headers: this._authHeaders()
        });
        if (!response.ok) throw new Error(`获取权限组权限列表失败：${response.status}。`);
        return response.json();
    },

    /**
     * 新增权限组权限。
     */
    async addGroupPermission(groupName, permission) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}/permissions`, {
            method: 'POST',
            headers: this._authHeaders({'Content-Type': 'application/json'}),
            body: JSON.stringify(permission)
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `新增权限组权限失败：${response.status}。`);
        }
        return response.json();
    },

    /**
     * 移除权限组权限。
     */
    async deleteGroupPermission(groupName, node, session) {
        let url = `${this.baseUrl}/groups/${encodeURIComponent(groupName)}/permissions/${encodeURIComponent(node)}`;
        if (session) {
            url += `?session=${encodeURIComponent(session)}`;
        }
        const response = await this._fetch(url, {
            method: 'DELETE',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `移除权限组权限失败：${response.status}。`);
        }
    },

    /**
     * 批量移除权限组权限。
     */
    async deleteGroupPermissions(groupName, nodes) {
        const results = [];
        for (const {node, session} of nodes) {
            try {
                await this.deleteGroupPermission(groupName, node, session);
            } catch (e) {
                results.push({node, error: e.message});
            }
        }
        return results;
    },

    /**
     * 新增用户权限组。
     */
    async addUserToGroup(userId, groupName) {
        const response = await this._fetch(`${this.baseUrl}/users/${encodeURIComponent(userId)}/groups/${encodeURIComponent(groupName)}`, {
            method: 'POST',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `新增用户权限组失败：${response.status}。`);
        }
    },

    /**
     * 移除用户权限组。
     */
    async removeUserFromGroup(userId, groupName) {
        const response = await this._fetch(`${this.baseUrl}/users/${encodeURIComponent(userId)}/groups/${encodeURIComponent(groupName)}`, {
            method: 'DELETE',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `移除用户权限组失败：${response.status}。`);
        }
    },

    /**
     * 为权限组新增父权限组。
     */
    async addGroupParent(groupName, parentName) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}/parents/${encodeURIComponent(parentName)}`, {
            method: 'POST',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `为权限组新增父权限组失败：${response.status}。`);
        }
    },

    /**
     * 从权限组移除父权限组。
     */
    async removeGroupParent(groupName, parentName) {
        const response = await this._fetch(`${this.baseUrl}/groups/${encodeURIComponent(groupName)}/parents/${encodeURIComponent(parentName)}`, {
            method: 'DELETE',
            headers: this._authHeaders()
        });
        if (!response.ok) {
            const e = await response.json().catch(() => ({}));
            throw new Error(e.message || `从权限组移除父权限组失败：${response.status}。`);
        }
    }
};