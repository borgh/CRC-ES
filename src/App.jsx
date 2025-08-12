import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { 
  FileText, 
  Send, 
  MessageSquare, 
  Mail, 
  Users, 
  BarChart3, 
  Settings, 
  LogOut, 
  Plus, 
  Search,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Shield,
  Activity
} from 'lucide-react'
import './App.css'

// Contexto de Autenticação
const AuthContext = React.createContext()

const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Provider de Autenticação
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simula verificação de token
    const token = localStorage.getItem('token')
    if (token) {
      setUser({
        id: 1,
        username: 'admin',
        email: 'admin@crces.org.br',
        role: 'admin',
        name: 'Administrador'
      })
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    // Simula login
    if (username === 'admin' && password === 'admin123') {
      const userData = {
        id: 1,
        username: 'admin',
        email: 'admin@crces.org.br',
        role: 'admin',
        name: 'Administrador'
      }
      setUser(userData)
      localStorage.setItem('token', 'demo-token-123')
      return { success: true }
    }
    return { success: false, error: 'Credenciais inválidas' }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

// Componente de Login
const LoginPage = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const result = await login(username, password)
    
    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">CRC-ES</CardTitle>
          <CardDescription>Sistema de Mensagens</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Usuário</label>
              <Input
                type="text"
                placeholder="Digite seu usuário"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Senha</label>
              <Input
                type="password"
                placeholder="Digite sua senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">Credenciais de teste:</p>
            <p className="text-sm text-gray-600">Usuário: <code className="bg-white px-1 rounded">admin</code></p>
            <p className="text-sm text-gray-600">Senha: <code className="bg-white px-1 rounded">admin123</code></p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Layout Principal
const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/campaigns', label: 'Campanhas', icon: Send },
    { path: '/templates', label: 'Templates', icon: FileText },
    { path: '/users', label: 'Usuários', icon: Users },
    { path: '/audit', label: 'Auditoria', icon: Shield },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">CRC-ES</h1>
              <p className="text-sm text-gray-500">Sistema de Mensagens</p>
            </div>
          </div>
        </div>
        
        <nav className="p-4">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <li key={item.path}>
                  <button
                    onClick={() => navigate(item.path)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                      isActive 
                        ? 'bg-indigo-100 text-indigo-700' 
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                </li>
              )
            })}
          </ul>
        </nav>
        
        <div className="absolute bottom-0 w-64 p-4 border-t">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <Users className="w-4 h-4 text-gray-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.role}</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={logout}
            className="w-full"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sair
          </Button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-gray-900">
              {menuItems.find(item => item.path === location.pathname)?.label || 'Dashboard'}
            </h2>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-green-600 border-green-200">
                Sistema Online
              </Badge>
              <div className="text-sm text-gray-500">
                {new Date().toLocaleDateString('pt-BR')}
              </div>
            </div>
          </div>
        </header>
        
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

// Dashboard
const Dashboard = () => {
  const statsData = [
    { name: 'Jan', emails: 1200, whatsapp: 800 },
    { name: 'Fev', emails: 1900, whatsapp: 1200 },
    { name: 'Mar', emails: 1500, whatsapp: 900 },
    { name: 'Abr', emails: 2200, whatsapp: 1500 },
    { name: 'Mai', emails: 1800, whatsapp: 1100 },
    { name: 'Jun', emails: 2500, whatsapp: 1800 },
  ]

  const pieData = [
    { name: 'Entregues', value: 85, color: '#10b981' },
    { name: 'Pendentes', value: 10, color: '#f59e0b' },
    { name: 'Falharam', value: 5, color: '#ef4444' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Enviadas</p>
                <p className="text-3xl font-bold text-gray-900">12,847</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Send className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm text-green-600 font-medium">+12%</span>
              <span className="text-sm text-gray-500 ml-2">vs mês anterior</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">WhatsApp</p>
                <p className="text-3xl font-bold text-gray-900">8,234</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm text-green-600 font-medium">+18%</span>
              <span className="text-sm text-gray-500 ml-2">vs mês anterior</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Emails</p>
                <p className="text-3xl font-bold text-gray-900">4,613</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Mail className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm text-green-600 font-medium">+8%</span>
              <span className="text-sm text-gray-500 ml-2">vs mês anterior</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Taxa Entrega</p>
                <p className="text-3xl font-bold text-gray-900">94.2%</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className="text-sm text-green-600 font-medium">+2.1%</span>
              <span className="text-sm text-gray-500 ml-2">vs mês anterior</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Mensagens por Mês</CardTitle>
            <CardDescription>Comparativo de envios por canal</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="emails" fill="#8b5cf6" name="Emails" />
                <Bar dataKey="whatsapp" fill="#10b981" name="WhatsApp" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status de Entrega</CardTitle>
            <CardDescription>Distribuição do status das mensagens</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Atividade Recente</CardTitle>
          <CardDescription>Últimas campanhas e envios</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { id: 1, action: 'Campanha "Cobrança Março" enviada', time: '2 min atrás', status: 'success' },
              { id: 2, action: 'Template "Lembrete Vencimento" criado', time: '15 min atrás', status: 'info' },
              { id: 3, action: 'Usuário "operador1" fez login', time: '1 hora atrás', status: 'info' },
              { id: 4, action: 'Campanha "Newsletter Abril" agendada', time: '2 horas atrás', status: 'warning' },
            ].map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'success' ? 'bg-green-500' :
                  activity.status === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                }`} />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Campanhas
const Campaigns = () => {
  const [campaigns] = useState([
    { id: 1, name: 'Cobrança Março 2024', type: 'email', status: 'completed', sent: 1250, delivered: 1180, failed: 70, created: '2024-03-15' },
    { id: 2, name: 'Lembrete Vencimento', type: 'whatsapp', status: 'running', sent: 800, delivered: 750, failed: 50, created: '2024-03-16' },
    { id: 3, name: 'Newsletter Abril', type: 'email', status: 'scheduled', sent: 0, delivered: 0, failed: 0, created: '2024-03-17' },
    { id: 4, name: 'Comunicado Urgente', type: 'whatsapp', status: 'draft', sent: 0, delivered: 0, failed: 0, created: '2024-03-18' },
  ])

  const getStatusBadge = (status) => {
    const variants = {
      completed: { variant: 'default', color: 'bg-green-100 text-green-800', label: 'Concluída' },
      running: { variant: 'default', color: 'bg-blue-100 text-blue-800', label: 'Executando' },
      scheduled: { variant: 'default', color: 'bg-yellow-100 text-yellow-800', label: 'Agendada' },
      draft: { variant: 'outline', color: 'bg-gray-100 text-gray-800', label: 'Rascunho' },
    }
    
    const config = variants[status] || variants.draft
    
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Gerenciar Campanhas</h3>
          <p className="text-sm text-gray-500">Crie e gerencie campanhas de envio em massa</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Nova Campanha
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Campanhas</CardTitle>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input placeholder="Buscar campanhas..." className="pl-10 w-64" />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Enviadas</TableHead>
                <TableHead>Entregues</TableHead>
                <TableHead>Falharam</TableHead>
                <TableHead>Criada em</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {campaigns.map((campaign) => (
                <TableRow key={campaign.id}>
                  <TableCell className="font-medium">{campaign.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {campaign.type === 'email' ? (
                        <Mail className="w-4 h-4 text-purple-600" />
                      ) : (
                        <MessageSquare className="w-4 h-4 text-green-600" />
                      )}
                      <span className="capitalize">{campaign.type}</span>
                    </div>
                  </TableCell>
                  <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                  <TableCell>{campaign.sent.toLocaleString()}</TableCell>
                  <TableCell>{campaign.delivered.toLocaleString()}</TableCell>
                  <TableCell>{campaign.failed.toLocaleString()}</TableCell>
                  <TableCell>{new Date(campaign.created).toLocaleDateString('pt-BR')}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// Templates
const Templates = () => {
  const [activeTab, setActiveTab] = useState('email')
  
  const emailTemplates = [
    { id: 1, name: 'Cobrança Mensalidade', subject: 'Mensalidade em Aberto - CRC-ES', created: '2024-03-10', used: 45 },
    { id: 2, name: 'Lembrete Vencimento', subject: 'Lembrete: Vencimento Próximo', created: '2024-03-12', used: 23 },
    { id: 3, name: 'Boas Vindas', subject: 'Bem-vindo ao CRC-ES', created: '2024-03-14', used: 12 },
  ]

  const whatsappTemplates = [
    { id: 1, name: 'Cobrança Rápida', preview: 'Olá {{nome}}, você possui mensalidade em aberto...', created: '2024-03-11', used: 67 },
    { id: 2, name: 'Confirmação Pagamento', preview: 'Pagamento confirmado! Obrigado {{nome}}...', created: '2024-03-13', used: 34 },
    { id: 3, name: 'Lembrete Geral', preview: 'Lembrete importante para {{nome}}...', created: '2024-03-15', used: 18 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Templates de Mensagens</h3>
          <p className="text-sm text-gray-500">Crie e gerencie templates reutilizáveis</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Novo Template
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="email">Templates de Email</TabsTrigger>
          <TabsTrigger value="whatsapp">Templates de WhatsApp</TabsTrigger>
        </TabsList>
        
        <TabsContent value="email" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Templates de Email</CardTitle>
              <CardDescription>Gerencie templates para campanhas de email</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>Assunto</TableHead>
                    <TableHead>Criado em</TableHead>
                    <TableHead>Usado</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {emailTemplates.map((template) => (
                    <TableRow key={template.id}>
                      <TableCell className="font-medium">{template.name}</TableCell>
                      <TableCell>{template.subject}</TableCell>
                      <TableCell>{new Date(template.created).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>{template.used}x</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="whatsapp" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Templates de WhatsApp</CardTitle>
              <CardDescription>Gerencie templates para campanhas de WhatsApp</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>Preview</TableHead>
                    <TableHead>Criado em</TableHead>
                    <TableHead>Usado</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {whatsappTemplates.map((template) => (
                    <TableRow key={template.id}>
                      <TableCell className="font-medium">{template.name}</TableCell>
                      <TableCell className="max-w-xs truncate">{template.preview}</TableCell>
                      <TableCell>{new Date(template.created).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>{template.used}x</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Usuários
const UsersPage = () => {
  const [users] = useState([
    { id: 1, name: 'Administrador', username: 'admin', email: 'admin@crces.org.br', role: 'admin', status: 'active', lastLogin: '2024-03-18T10:30:00' },
    { id: 2, name: 'João Silva', username: 'joao.silva', email: 'joao@crces.org.br', role: 'supervisor', status: 'active', lastLogin: '2024-03-17T14:20:00' },
    { id: 3, name: 'Maria Santos', username: 'maria.santos', email: 'maria@crces.org.br', role: 'operator', status: 'active', lastLogin: '2024-03-16T09:15:00' },
    { id: 4, name: 'Pedro Costa', username: 'pedro.costa', email: 'pedro@crces.org.br', role: 'operator', status: 'inactive', lastLogin: '2024-03-10T16:45:00' },
  ])

  const getRoleBadge = (role) => {
    const variants = {
      admin: { color: 'bg-red-100 text-red-800', label: 'Administrador' },
      supervisor: { color: 'bg-blue-100 text-blue-800', label: 'Supervisor' },
      operator: { color: 'bg-green-100 text-green-800', label: 'Operador' },
      viewer: { color: 'bg-gray-100 text-gray-800', label: 'Visualizador' },
    }
    
    const config = variants[role] || variants.viewer
    
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    )
  }

  const getStatusBadge = (status) => {
    return (
      <Badge className={status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
        {status === 'active' ? 'Ativo' : 'Inativo'}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Gerenciar Usuários</h3>
          <p className="text-sm text-gray-500">Controle de acesso e permissões</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Novo Usuário
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Usuários do Sistema</CardTitle>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input placeholder="Buscar usuários..." className="pl-10 w-64" />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Usuário</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Função</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Último Login</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.name}</TableCell>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{getRoleBadge(user.role)}</TableCell>
                  <TableCell>{getStatusBadge(user.status)}</TableCell>
                  <TableCell>{new Date(user.lastLogin).toLocaleString('pt-BR')}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// Auditoria
const Audit = () => {
  const [auditLogs] = useState([
    { id: 1, user: 'admin', action: 'LOGIN', resource: 'Sistema', description: 'Login realizado com sucesso', ip: '192.168.1.100', timestamp: '2024-03-18T10:30:00', success: true },
    { id: 2, user: 'joao.silva', action: 'CREATE_CAMPAIGN', resource: 'Campanha', description: 'Campanha "Cobrança Março" criada', ip: '192.168.1.101', timestamp: '2024-03-18T09:15:00', success: true },
    { id: 3, user: 'maria.santos', action: 'SEND_EMAIL', resource: 'Email', description: 'Email enviado para cliente@email.com', ip: '192.168.1.102', timestamp: '2024-03-18T08:45:00', success: true },
    { id: 4, user: 'pedro.costa', action: 'LOGIN', resource: 'Sistema', description: 'Tentativa de login falhada', ip: '192.168.1.103', timestamp: '2024-03-18T08:30:00', success: false },
    { id: 5, user: 'admin', action: 'CREATE_USER', resource: 'Usuário', description: 'Usuário "operador2" criado', ip: '192.168.1.100', timestamp: '2024-03-17T16:20:00', success: true },
  ])

  const getActionBadge = (action, success) => {
    const baseColor = success ? 'text-green-800 bg-green-100' : 'text-red-800 bg-red-100'
    
    return (
      <Badge className={baseColor}>
        {action.replace('_', ' ')}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Logs de Auditoria</h3>
          <p className="text-sm text-gray-500">Rastreamento de todas as ações do sistema</p>
        </div>
        <div className="flex items-center space-x-2">
          <Select defaultValue="all">
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filtrar por ação" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas as ações</SelectItem>
              <SelectItem value="login">Login</SelectItem>
              <SelectItem value="campaign">Campanhas</SelectItem>
              <SelectItem value="email">Emails</SelectItem>
              <SelectItem value="user">Usuários</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Registro de Atividades</CardTitle>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input placeholder="Buscar logs..." className="pl-10 w-64" />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuário</TableHead>
                <TableHead>Ação</TableHead>
                <TableHead>Recurso</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>IP</TableHead>
                <TableHead>Data/Hora</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {auditLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-medium">{log.user}</TableCell>
                  <TableCell>{getActionBadge(log.action, log.success)}</TableCell>
                  <TableCell>{log.resource}</TableCell>
                  <TableCell className="max-w-xs truncate">{log.description}</TableCell>
                  <TableCell>{log.ip}</TableCell>
                  <TableCell>{new Date(log.timestamp).toLocaleString('pt-BR')}</TableCell>
                  <TableCell>
                    {log.success ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// Componente de Rota Protegida
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando...</p>
        </div>
      </div>
    )
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return <Layout>{children}</Layout>
}

// Componente Principal
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/campaigns" element={
              <ProtectedRoute>
                <Campaigns />
              </ProtectedRoute>
            } />
            <Route path="/templates" element={
              <ProtectedRoute>
                <Templates />
              </ProtectedRoute>
            } />
            <Route path="/users" element={
              <ProtectedRoute>
                <UsersPage />
              </ProtectedRoute>
            } />
            <Route path="/audit" element={
              <ProtectedRoute>
                <Audit />
              </ProtectedRoute>
            } />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

