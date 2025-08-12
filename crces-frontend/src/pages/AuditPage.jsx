import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Search,
  Shield,
  User,
  Mail,
  MessageSquare,
  Settings,
  AlertTriangle,
} from 'lucide-react'

const mockAuditLogs = [
  {
    id: 1,
    username: 'admin',
    action: 'LOGIN',
    resource: 'Sistema',
    description: 'Login realizado com sucesso',
    ipAddress: '192.168.1.100',
    timestamp: '2024-03-15T10:30:00Z',
    success: true,
  },
  {
    id: 2,
    username: 'operador1',
    action: 'CREATE_CAMPAIGN',
    resource: 'Campanha',
    description: 'Criou campanha "Cobrança Mensalidade Março"',
    ipAddress: '192.168.1.101',
    timestamp: '2024-03-15T09:15:00Z',
    success: true,
  },
  {
    id: 3,
    username: 'supervisor',
    action: 'DELETE_USER',
    resource: 'Usuário',
    description: 'Tentativa de exclusão de usuário negada',
    ipAddress: '192.168.1.102',
    timestamp: '2024-03-14T16:45:00Z',
    success: false,
  },
  {
    id: 4,
    username: 'admin',
    action: 'UPDATE_TEMPLATE',
    resource: 'Template',
    description: 'Atualizou template de email "Cobrança Mensalidade"',
    ipAddress: '192.168.1.100',
    timestamp: '2024-03-14T14:20:00Z',
    success: true,
  },
]

export default function AuditPage() {
  const [auditLogs, setAuditLogs] = useState(mockAuditLogs)
  const [searchTerm, setSearchTerm] = useState('')
  const [actionFilter, setActionFilter] = useState('all')

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = 
      log.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesAction = actionFilter === 'all' || log.action === actionFilter
    return matchesSearch && matchesAction
  })

  const getActionIcon = (action) => {
    switch (action) {
      case 'LOGIN':
        return <User className="h-4 w-4" />
      case 'CREATE_CAMPAIGN':
      case 'UPDATE_CAMPAIGN':
        return <Mail className="h-4 w-4" />
      case 'CREATE_TEMPLATE':
      case 'UPDATE_TEMPLATE':
        return <MessageSquare className="h-4 w-4" />
      case 'DELETE_USER':
      case 'CREATE_USER':
        return <Shield className="h-4 w-4" />
      default:
        return <Settings className="h-4 w-4" />
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Auditoria
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Visualize logs de atividades e ações do sistema
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Buscar logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={actionFilter} onValueChange={setActionFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filtrar por ação" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as ações</SelectItem>
                <SelectItem value="LOGIN">Login</SelectItem>
                <SelectItem value="CREATE_CAMPAIGN">Criar Campanha</SelectItem>
                <SelectItem value="UPDATE_CAMPAIGN">Atualizar Campanha</SelectItem>
                <SelectItem value="CREATE_TEMPLATE">Criar Template</SelectItem>
                <SelectItem value="UPDATE_TEMPLATE">Atualizar Template</SelectItem>
                <SelectItem value="DELETE_USER">Excluir Usuário</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Audit Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle>Logs de Auditoria</CardTitle>
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
                <TableHead>Status</TableHead>
                <TableHead>Data/Hora</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-medium">
                    <div className="flex items-center space-x-2">
                      <User className="h-4 w-4" />
                      <span>{log.username}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getActionIcon(log.action)}
                      <span className="text-sm">{log.action}</span>
                    </div>
                  </TableCell>
                  <TableCell>{log.resource}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {log.description}
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {log.ipAddress}
                  </TableCell>
                  <TableCell>
                    <Badge variant={log.success ? 'default' : 'destructive'}>
                      {log.success ? 'Sucesso' : 'Falha'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {formatDate(log.timestamp)}
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

