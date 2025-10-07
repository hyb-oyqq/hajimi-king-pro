import axios from 'axios'

const API_BASE_URL = '/api'

class ApiService {
  constructor() {
    this.authKey = ''
  }

  setAuthKey(key) {
    this.authKey = key
  }

  getHeaders() {
    return {
      'X-Auth-Key': this.authKey,
      'Content-Type': 'application/json'
    }
  }

  // Dashboard APIs
  async getDashboardStats() {
    const response = await axios.get(`${API_BASE_URL}/dashboard/stats`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Keys APIs
  async getKeys(params = {}) {
    const response = await axios.get(`${API_BASE_URL}/keys`, {
      headers: this.getHeaders(),
      params
    })
    return response.data
  }

  async deleteKey(keyId) {
    const response = await axios.delete(`${API_BASE_URL}/keys/${keyId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Analytics APIs
  async getAnalyticsTrend(days = 30) {
    const response = await axios.get(`${API_BASE_URL}/analytics/trend`, {
      headers: this.getHeaders(),
      params: { days }
    })
    return response.data
  }

  async getRepoStats() {
    const response = await axios.get(`${API_BASE_URL}/analytics/repo-stats`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Logs APIs
  async getLogs(lines = 200) {
    const response = await axios.get(`${API_BASE_URL}/logs`, {
      headers: this.getHeaders(),
      params: { lines }
    })
    return response.data
  }

  async getLiveLogs() {
    const response = await axios.get(`${API_BASE_URL}/logs/live`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Rules APIs
  async getRules() {
    const response = await axios.get(`${API_BASE_URL}/rules`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async addRule(rule) {
    const response = await axios.post(`${API_BASE_URL}/rules`, 
      { rule },
      { headers: this.getHeaders() }
    )
    return response.data
  }

  async deleteRule(index) {
    const response = await axios.delete(`${API_BASE_URL}/rules/${index}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async restartSystem() {
    const response = await axios.post(`${API_BASE_URL}/system/restart`, {}, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Settings APIs
  async getSettings() {
    const response = await axios.get(`${API_BASE_URL}/settings`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getGithubTokens() {
    const response = await axios.get(`${API_BASE_URL}/settings/github-tokens`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async addGithubToken(token) {
    const response = await axios.post(`${API_BASE_URL}/settings/github-tokens`,
      { token },
      { headers: this.getHeaders() }
    )
    return response.data
  }

  async deleteGithubToken(index) {
    const response = await axios.delete(`${API_BASE_URL}/settings/github-tokens/${index}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getGithubSessions() {
    const response = await axios.get(`${API_BASE_URL}/settings/github-sessions`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async addGithubSession(session) {
    const response = await axios.post(`${API_BASE_URL}/settings/github-sessions`,
      { session },
      { headers: this.getHeaders() }
    )
    return response.data
  }

  async deleteGithubSession(index) {
    const response = await axios.delete(`${API_BASE_URL}/settings/github-sessions/${index}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // System APIs
  async getSystemStatus() {
    const response = await axios.get(`${API_BASE_URL}/system/status`, {
      headers: this.getHeaders()
    })
    return response.data
  }
}

const api = new ApiService()
export default api

