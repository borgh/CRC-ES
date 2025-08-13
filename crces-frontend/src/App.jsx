import React, { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  User, 
  Mail, 
  MessageCircle, 
  Settings, 
  Users, 
  FileText, 
  BarChart3, 
  LogOut, 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  Pause, 
  Eye,
  Database,
  Shield,
  Activity,
  Send,
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Home,
  Menu,
  X
} from 'lucide-react'
import './App.css'

// Context de Autenticação
const AuthContext = createContext()

const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}

// Configuração da API
const API_BASE = 'http://localhost:5003/api'

const api = {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token')
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      },
      ...options
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, config)
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.message || 'Erro na requisição')
      }
      
      return data
    } catch (error) {
      console.error('Erro na API:', error)
      throw error
    }
  },

  // Auth
  login: (credentials) => api.request('/auth/login', { method: 'POST', body: credentials }),
  logout: () => api.request('/auth/logout', { method: 'POST' }),
  getCurrentUser: () => api.request('/auth/me'),

  // Campanhas
  getCampaigns: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.request(`/campaigns${query ? `?${query}` : ''}`)
  },
  createCampaign: (data) => api.request('/campaigns', { method: 'POST', body: data }),
  updateCampaign: (id, data) => api.request(`/campaigns/${id}`, { method: 'PUT', body: data }),
  deleteCampaign: (id) => api.request(`/campaigns/${id}`, { method: 'DELETE' }),
  startCampaign: (id) => api.request(`/campaigns/${id}/start`, { method: 'POST' }),
  stopCampaign: (id) => api.request(`/campaigns/${id}/stop`, { method: 'POST' }),
  getCampaignStats: () => api.request('/campaigns/stats'),

  // Templates
  getTemplates: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.request(`/templates${query ? `?${query}` : ''}`)
  },
  createTemplate: (data) => api.request('/templates', { method: 'POST', body: data }),
  updateTemplate: (id, data) => api.request(`/templates/${id}`, { method: 'PUT', body: data }),
  deleteTemplate: (id) => api.request(`/templates/${id}`, { method: 'DELETE' }),
  previewTemplate: (id, data) => api.request(`/templates/${id}/preview`, { method: 'POST', body: data }),
  getVariables: () => api.request('/templates/variables'),
  createDefaultTemplates: () => api.request('/templates/defaults', { method: 'POST' }),

  // Contatos
  getContacts: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.request(`/contacts${query ? `?${query}` : ''}`)
  },
  syncContacts: () => api.request('/contacts/sync', { method: 'POST' }),
  getDevedores: () => api.request('/contacts/devedores'),
  getAnuidadeContacts: () => api.request('/contacts/anuidade'),
  searchByPhone: (phone) => api.request('/contacts/search-by-phone', { method: 'POST', body: { phone } }),
  getContactsStats: () => api.request('/contacts/stats'),

  // Configurações
  getConfigs: () => api.request('/config'),
  updateConfig: (key, data) => api.request(`/config/${key}`, { method: 'PUT', body: data }),
  getDatabaseConfig: () => api.request('/config/database'),
  updateDatabaseConfig: (data) => api.request('/config/database', { method: 'PUT', body: data }),
  testDatabase: () => api.request('/config/database/test', { method: 'POST' }),
  testEmail: () => api.request('/config/email/test', { method: 'POST' }),
  testWhatsApp: () => api.request('/config/whatsapp/test', { method: 'POST' }),

  // Auditoria
  getAuditLogs: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.request(`/audit${query ? `?${query}` : ''}`)
  },
  getAuditStats: () => api.request('/audit/stats'),
  exportAuditLogs: (data) => api.request('/audit/export', { method: 'POST', body: data })
}

// Provider de Autenticação
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.getCurrentUser()
        .then(response => setUser(response.data))
        .catch(() => {
          localStorage.removeItem('token')
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (credentials) => {
    try {
      const response = await api.login(credentials)
      localStorage.setItem('token', response.data.access_token)
      setUser(response.data.user)
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    }
  }

  const logout = async () => {
    try {
      await api.logout()
    } catch (error) {
      console.error('Erro no logout:', error)
    } finally {
      localStorage.removeItem('token')
      setUser(null)
    }
  }

  const value = {
    user,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Componente de Rota Protegida
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" replace />
}

// Componente de Login
const LoginPage = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const result = await login(credentials)
    
    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.message)
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-blue-900">Sistema CRC-ES</CardTitle>
          <CardDescription>Gestão de Campanhas de Comunicação</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}
            
            <div>
              <Input
                type="text"
                placeholder="Usuário"
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                required
              />
            </div>
            
            <div>
              <Input
                type="password"
                placeholder="Senha"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                required
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          
          <div className="mt-4 text-center text-sm text-gray-600">
            <p>Credenciais padrão:</p>
            <p><strong>Usuário:</strong> admin</p>
            <p><strong>Senha:</strong> admin123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Layout Principal
const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  const location = useLocation()

  const menuItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/campaigns', icon: Send, label: 'Campanhas' },
    { path: '/templates', icon: FileText, label: 'Templates' },
    { path: '/contacts', icon: Users, label: 'Contatos' },
    { path: '/config', icon: Settings, label: 'Configurações' },
    { path: '/audit', icon: Shield, label: 'Auditoria' }
  ]

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between h-16 px-4 bg-blue-900 text-white">
          <h1 className="text-lg font-semibold">CRC-ES</h1>
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden text-white hover:bg-blue-800"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <nav className="mt-4">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <a
                key={item.path}
                href={item.path}
                className={`flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-900 transition-colors ${
                  isActive ? 'bg-blue-50 text-blue-900 border-r-2 border-blue-900' : ''
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon className="h-5 w-5 mr-3" />
                {item.label}
              </a>
            )
          })}
        </nav>
        
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <User className="h-8 w-8 text-gray-400" />
              <div className="ml-2">
                <p className="text-sm font-medium text-gray-900">{user?.username}</p>
                <p className="text-xs text-gray-500">{user?.is_admin ? 'Administrador' : 'Usuário'}</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Overlay para mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b h-16 flex items-center justify-between px-4">
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-4 w-4" />
          </Button>
          
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="text-green-700 border-green-200">
              Sistema Online
            </Badge>
          </div>
        </header>

        {/* Conteúdo */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

// Página Dashboard
const Dashboard = () => {
  const [stats, setStats] = useState({
    campaigns: { total: 0, running: 0, completed: 0 },
    contacts: { total: 0, with_email: 0, with_phone: 0 },
    recent_activity: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [campaignStats, contactStats] = await Promise.all([
          api.getCampaignStats(),
          api.getContactsStats()
        ])
        
        setStats({
          campaigns: campaignStats.data,
          contacts: contactStats.data,
          recent_activity: []
        })
      } catch (error) {
        console.error('Erro ao carregar estatísticas:', error)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Visão geral do sistema CRC-ES</p>
      </div>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total de Campanhas</p>
                <p className="text-2xl font-bold text-gray-900">{stats.campaigns.total}</p>
              </div>
              <Send className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Campanhas Ativas</p>
                <p className="text-2xl font-bold text-green-600">{stats.campaigns.running}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total de Contatos</p>
                <p className="text-2xl font-bold text-gray-900">{stats.contacts.total}</p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Taxa de Sucesso</p>
                <p className="text-2xl font-bold text-green-600">{stats.campaigns.success_rate || 0}%</p>
              </div>
              <BarChart3 className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Ações Rápidas */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
          <CardDescription>Acesse rapidamente as funcionalidades principais</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-20 flex flex-col items-center justify-center space-y-2" asChild>
              <a href="/campaigns">
                <Plus className="h-6 w-6" />
                <span>Nova Campanha</span>
              </a>
            </Button>
            
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2" asChild>
              <a href="/templates">
                <FileText className="h-6 w-6" />
                <span>Gerenciar Templates</span>
              </a>
            </Button>
            
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2" asChild>
              <a href="/contacts">
                <Users className="h-6 w-6" />
                <span>Sincronizar Contatos</span>
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Página de Campanhas
const CampaignsPage = () => {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [editingCampaign, setEditingCampaign] = useState(null)
  const [templates, setTemplates] = useState([])

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'email',
    email_template_id: '',
    whatsapp_template_id: ''
  })

  useEffect(() => {
    loadCampaigns()
    loadTemplates()
  }, [])

  const loadCampaigns = async () => {
    try {
      const response = await api.getCampaigns()
      setCampaigns(response.data.campaigns || [])
    } catch (error) {
      console.error('Erro ao carregar campanhas:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await api.getTemplates()
      setTemplates(response.data.templates || [])
    } catch (error) {
      console.error('Erro ao carregar templates:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (editingCampaign) {
        await api.updateCampaign(editingCampaign.id, formData)
      } else {
        await api.createCampaign(formData)
      }
      
      setShowCreateDialog(false)
      setEditingCampaign(null)
      setFormData({ name: '', description: '', type: 'email', email_template_id: '', whatsapp_template_id: '' })
      loadCampaigns()
    } catch (error) {
      console.error('Erro ao salvar campanha:', error)
      alert('Erro ao salvar campanha: ' + error.message)
    }
  }

  const handleEdit = (campaign) => {
    setEditingCampaign(campaign)
    setFormData({
      name: campaign.name,
      description: campaign.description,
      type: campaign.type,
      email_template_id: campaign.email_template_id || '',
      whatsapp_template_id: campaign.whatsapp_template_id || ''
    })
    setShowCreateDialog(true)
  }

  const handleDelete = async (id) => {
    if (confirm('Tem certeza que deseja excluir esta campanha?')) {
      try {
        await api.deleteCampaign(id)
        loadCampaigns()
      } catch (error) {
        console.error('Erro ao excluir campanha:', error)
        alert('Erro ao excluir campanha: ' + error.message)
      }
    }
  }

  const handleStart = async (id) => {
    try {
      await api.startCampaign(id)
      loadCampaigns()
    } catch (error) {
      console.error('Erro ao iniciar campanha:', error)
      alert('Erro ao iniciar campanha: ' + error.message)
    }
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { label: 'Rascunho', variant: 'secondary' },
      scheduled: { label: 'Agendada', variant: 'outline' },
      running: { label: 'Executando', variant: 'default' },
      completed: { label: 'Concluída', variant: 'success' },
      failed: { label: 'Falhou', variant: 'destructive' },
      cancelled: { label: 'Cancelada', variant: 'secondary' }
    }
    
    const config = statusConfig[status] || statusConfig.draft
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campanhas</h1>
          <p className="text-gray-600">Gerencie suas campanhas de email e WhatsApp</p>
        </div>
        
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button onClick={() => {
              setEditingCampaign(null)
              setFormData({ name: '', description: '', type: 'email', email_template_id: '', whatsapp_template_id: '' })
            }}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Campanha
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{editingCampaign ? 'Editar Campanha' : 'Nova Campanha'}</DialogTitle>
              <DialogDescription>
                {editingCampaign ? 'Edite os dados da campanha' : 'Crie uma nova campanha de comunicação'}
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Input
                  placeholder="Nome da campanha"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Textarea
                  placeholder="Descrição (opcional)"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              
              <div>
                <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Tipo de campanha" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="whatsapp">WhatsApp</SelectItem>
                    <SelectItem value="both">Email + WhatsApp</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {(formData.type === 'email' || formData.type === 'both') && (
                <div>
                  <Select value={formData.email_template_id} onValueChange={(value) => setFormData({ ...formData, email_template_id: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Template de email" />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.filter(t => t.type === 'email').map(template => (
                        <SelectItem key={template.id} value={template.id.toString()}>
                          {template.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              {(formData.type === 'whatsapp' || formData.type === 'both') && (
                <div>
                  <Select value={formData.whatsapp_template_id} onValueChange={(value) => setFormData({ ...formData, whatsapp_template_id: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Template de WhatsApp" />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.filter(t => t.type === 'whatsapp').map(template => (
                        <SelectItem key={template.id} value={template.id.toString()}>
                          {template.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  {editingCampaign ? 'Salvar' : 'Criar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Lista de Campanhas */}
      <div className="grid gap-4">
        {campaigns.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <Send className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma campanha encontrada</h3>
              <p className="text-gray-600 mb-4">Crie sua primeira campanha de comunicação</p>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Campanha
              </Button>
            </CardContent>
          </Card>
        ) : (
          campaigns.map(campaign => (
            <Card key={campaign.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{campaign.name}</h3>
                      {getStatusBadge(campaign.status)}
                      <Badge variant="outline">{campaign.type}</Badge>
                    </div>
                    
                    {campaign.description && (
                      <p className="text-gray-600 mb-2">{campaign.description}</p>
                    )}
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      {campaign.sent_count > 0 && (
                        <span>Enviados: {campaign.sent_count}</span>
                      )}
                      {campaign.delivered_count > 0 && (
                        <span>Entregues: {campaign.delivered_count}</span>
                      )}
                      {campaign.created_at && (
                        <span>Criada em: {new Date(campaign.created_at).toLocaleDateString('pt-BR')}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {campaign.status === 'draft' && (
                      <Button size="sm" onClick={() => handleStart(campaign.id)}>
                        <Play className="h-4 w-4 mr-1" />
                        Iniciar
                      </Button>
                    )}
                    
                    <Button size="sm" variant="outline" onClick={() => handleEdit(campaign)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    
                    <Button size="sm" variant="outline" onClick={() => handleDelete(campaign.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

// Componente principal da aplicação
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/campaigns" element={
            <ProtectedRoute>
              <Layout>
                <CampaignsPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/templates" element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h2 className="text-xl font-medium text-gray-900 mb-2">Templates</h2>
                  <p className="text-gray-600">Funcionalidade em desenvolvimento</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/contacts" element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h2 className="text-xl font-medium text-gray-900 mb-2">Contatos</h2>
                  <p className="text-gray-600">Funcionalidade em desenvolvimento</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/config" element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h2 className="text-xl font-medium text-gray-900 mb-2">Configurações</h2>
                  <p className="text-gray-600">Funcionalidade em desenvolvimento</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/audit" element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h2 className="text-xl font-medium text-gray-900 mb-2">Auditoria</h2>
                  <p className="text-gray-600">Funcionalidade em desenvolvimento</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

