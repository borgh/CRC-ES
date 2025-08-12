import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Plus,
  Search,
  MoreHorizontal,
  Play,
  Pause,
  Eye,
  Edit,
  Trash2,
  Mail,
  MessageSquare,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react'

// Dados mockados
const mockCampaigns = [
  {
    id: 1,
    name: 'Cobrança Mensalidade Março 2024',
    type: 'email',
    status: 'completed',
    totalRecipients: 1234,
    sent: 1234,
    delivered: 1198,
    opened: 856,
    clicked: 234,
    createdAt: '2024-03-15T10:30:00Z',
    scheduledAt: null,
    completedAt: '2024-03-15T14:45:00Z',
  },
  {
    id: 2,
    name: 'Lembrete Vencimento WhatsApp',
    type: 'whatsapp',
    status: 'running',
    totalRecipients: 567,
    sent: 234,
    delivered: 220,
    opened: 0,
    clicked: 0,
    createdAt: '2024-03-14T09:15:00Z',
    scheduledAt: null,
    completedAt: null,
  },
  {
    id: 3,
    name: 'Comunicado Assembleia Geral',
    type: 'email',
    status: 'scheduled',
    totalRecipients: 2100,
    sent: 0,
    delivered: 0,
    opened: 0,
    clicked: 0,
    createdAt: '2024-03-13T16:20:00Z',
    scheduledAt: '2024-03-20T08:00:00Z',
    completedAt: null,
  },
  {
    id: 4,
    name: 'Cobrança Anuidade 2024',
    type: 'email',
    status: 'draft',
    totalRecipients: 0,
    sent: 0,
    delivered: 0,
    opened: 0,
    clicked: 0,
    createdAt: '2024-03-12T11:45:00Z',
    scheduledAt: null,
    completedAt: null,
  },
]

export default function CampaignsPage() {
  const { apiRequest } = useAuth()
  const [campaigns, setCampaigns] = useState(mockCampaigns)
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('all')

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'scheduled':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      case 'draft':
        return <Edit className="h-4 w-4 text-gray-500" />
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
      case 'draft':
        return 'Rascunho'
      case 'failed':
        return 'Falhou'
      default:
        return 'Desconhecido'
    }
  }

  const getStatusVariant = (status) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'running':
        return 'secondary'
      case 'scheduled':
        return 'outline'
      case 'draft':
        return 'secondary'
      case 'failed':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'all' || 
                     (activeTab === 'email' && campaign.type === 'email') ||
                     (activeTab === 'whatsapp' && campaign.type === 'whatsapp')
    return matchesSearch && matchesTab
  })

  const handleCreateCampaign = () => {
    // TODO: Implementar criação de campanha
    console.log('Criar nova campanha')
  }

  const handleViewCampaign = (campaignId) => {
    // TODO: Implementar visualização de campanha
    console.log('Ver campanha:', campaignId)
  }

  const handleEditCampaign = (campaignId) => {
    // TODO: Implementar edição de campanha
    console.log('Editar campanha:', campaignId)
  }

  const handleDeleteCampaign = (campaignId) => {
    // TODO: Implementar exclusão de campanha
    console.log('Excluir campanha:', campaignId)
  }

  const handleStartCampaign = (campaignId) => {
    // TODO: Implementar início de campanha
    console.log('Iniciar campanha:', campaignId)
  }

  const handlePauseCampaign = (campaignId) => {
    // TODO: Implementar pausa de campanha
    console.log('Pausar campanha:', campaignId)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Campanhas
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Gerencie suas campanhas de email e WhatsApp
          </p>
        </div>
        <Button onClick={handleCreateCampaign}>
          <Plus className="h-4 w-4 mr-2" />
          Nova Campanha
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Buscar campanhas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Campaigns Table */}
      <Card>
        <CardHeader>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all">Todas</TabsTrigger>
              <TabsTrigger value="email">
                <Mail className="h-4 w-4 mr-2" />
                Email
              </TabsTrigger>
              <TabsTrigger value="whatsapp">
                <MessageSquare className="h-4 w-4 mr-2" />
                WhatsApp
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Destinatários</TableHead>
                <TableHead>Enviadas</TableHead>
                <TableHead>Entregues</TableHead>
                <TableHead>Criada em</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredCampaigns.map((campaign) => (
                <TableRow key={campaign.id}>
                  <TableCell className="font-medium">
                    {campaign.name}
                  </TableCell>
                  <TableCell>
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
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(campaign.status)}
                      <Badge variant={getStatusVariant(campaign.status)}>
                        {getStatusText(campaign.status)}
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell>{campaign.totalRecipients.toLocaleString()}</TableCell>
                  <TableCell>{campaign.sent.toLocaleString()}</TableCell>
                  <TableCell>{campaign.delivered.toLocaleString()}</TableCell>
                  <TableCell>{formatDate(campaign.createdAt)}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Ações</DropdownMenuLabel>
                        <DropdownMenuItem onClick={() => handleViewCampaign(campaign.id)}>
                          <Eye className="mr-2 h-4 w-4" />
                          Visualizar
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleEditCampaign(campaign.id)}>
                          <Edit className="mr-2 h-4 w-4" />
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        {campaign.status === 'draft' && (
                          <DropdownMenuItem onClick={() => handleStartCampaign(campaign.id)}>
                            <Play className="mr-2 h-4 w-4" />
                            Iniciar
                          </DropdownMenuItem>
                        )}
                        {campaign.status === 'running' && (
                          <DropdownMenuItem onClick={() => handlePauseCampaign(campaign.id)}>
                            <Pause className="mr-2 h-4 w-4" />
                            Pausar
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => handleDeleteCampaign(campaign.id)}
                          className="text-red-600 dark:text-red-400"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
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

