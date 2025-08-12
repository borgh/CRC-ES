import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts'
import {
  Send,
  Mail,
  MessageSquare,
  Users,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react'

// Dados mockados para demonstração
const mockStats = {
  totalCampaigns: 45,
  activeCampaigns: 8,
  totalMessages: 12543,
  successRate: 94.2,
  emailsSent: 8234,
  whatsappSent: 4309,
  pendingMessages: 156,
  failedMessages: 89,
}

const mockCampaignData = [
  { name: 'Jan', emails: 1200, whatsapp: 800 },
  { name: 'Fev', emails: 1900, whatsapp: 1200 },
  { name: 'Mar', emails: 1500, whatsapp: 900 },
  { name: 'Abr', emails: 2100, whatsapp: 1400 },
  { name: 'Mai', emails: 1800, whatsapp: 1100 },
  { name: 'Jun', emails: 2400, whatsapp: 1600 },
]

const mockStatusData = [
  { name: 'Entregues', value: 89, color: '#10b981' },
  { name: 'Pendentes', value: 7, color: '#f59e0b' },
  { name: 'Falharam', value: 4, color: '#ef4444' },
]

const mockRecentCampaigns = [
  {
    id: 1,
    name: 'Cobrança Mensalidade Março',
    type: 'email',
    status: 'completed',
    sent: 1234,
    delivered: 1198,
    createdAt: '2024-03-15',
  },
  {
    id: 2,
    name: 'Lembrete Vencimento',
    type: 'whatsapp',
    status: 'running',
    sent: 567,
    delivered: 534,
    createdAt: '2024-03-14',
  },
  {
    id: 3,
    name: 'Comunicado Importante',
    type: 'email',
    status: 'scheduled',
    sent: 0,
    delivered: 0,
    createdAt: '2024-03-13',
  },
]

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState(mockStats)
  const [loading, setLoading] = useState(false)

  // Função para buscar estatísticas (mockada)
  const fetchStats = async () => {
    setLoading(true)
    // Simula chamada à API
    setTimeout(() => {
      setStats(mockStats)
      setLoading(false)
    }, 1000)
  }

  useEffect(() => {
    fetchStats()
  }, [])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'scheduled':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Concluída'
      case 'running':
        return 'Em andamento'
      case 'scheduled':
        return 'Agendada'
      case 'failed':
        return 'Falhou'
      default:
        return 'Desconhecido'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Bem-vindo de volta, {user?.username}! Aqui está um resumo das suas campanhas.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Campanhas</CardTitle>
            <Send className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCampaigns}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                +12% desde o mês passado
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Campanhas Ativas</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeCampaigns}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-blue-600">Em execução agora</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Mensagens Enviadas</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMessages.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                +8% desde o mês passado
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.successRate}%</div>
            <Progress value={stats.successRate} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Campaign Performance Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Performance das Campanhas</CardTitle>
            <CardDescription>
              Comparativo de envios por email e WhatsApp nos últimos 6 meses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockCampaignData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="emails" fill="#3b82f6" name="Emails" />
                <Bar dataKey="whatsapp" fill="#10b981" name="WhatsApp" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Status das Mensagens</CardTitle>
            <CardDescription>
              Distribuição do status das mensagens enviadas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={mockStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {mockStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {mockStatusData.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Campaigns */}
      <Card>
        <CardHeader>
          <CardTitle>Campanhas Recentes</CardTitle>
          <CardDescription>
            Últimas campanhas criadas e seus status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockRecentCampaigns.map((campaign) => (
              <div
                key={campaign.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(campaign.status)}
                    <div>
                      <h4 className="font-medium">{campaign.name}</h4>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Badge variant={campaign.type === 'email' ? 'default' : 'secondary'}>
                          {campaign.type === 'email' ? (
                            <>
                              <Mail className="h-3 w-3 mr-1" />
                              Email
                            </>
                          ) : (
                            <>
                              <MessageSquare className="h-3 w-3 mr-1" />
                              WhatsApp
                            </>
                          )}
                        </Badge>
                        <span>{getStatusText(campaign.status)}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {campaign.sent > 0 ? `${campaign.sent} enviadas` : 'Não iniciada'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {campaign.delivered > 0 && `${campaign.delivered} entregues`}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

