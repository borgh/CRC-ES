import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  LayoutDashboard,
  Send,
  FileText,
  Users,
  Shield,
  User,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Building2,
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    permission: 'view_dashboard',
  },
  {
    name: 'Campanhas',
    href: '/campaigns',
    icon: Send,
    permission: 'view_dashboard',
  },
  {
    name: 'Templates',
    href: '/templates',
    icon: FileText,
    permission: 'view_dashboard',
  },
  {
    name: 'Usuários',
    href: '/users',
    icon: Users,
    permission: 'manage_users',
  },
  {
    name: 'Auditoria',
    href: '/audit',
    icon: Shield,
    permission: 'view_audit_logs',
  },
]

export default function Sidebar({ isOpen, onToggle }) {
  const location = useLocation()
  const { user, logout } = useAuth()

  // Verifica se o usuário tem permissão para acessar um item
  const hasPermission = (permission) => {
    if (!user || !user.permissions) return false
    return user.permissions.includes(permission)
  }

  // Filtra itens de navegação baseado nas permissões
  const filteredNavigation = navigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  )

  return (
    <div className={cn(
      "bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 flex flex-col",
      isOpen ? "w-64" : "w-16"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className={cn(
          "flex items-center space-x-3 transition-opacity duration-300",
          isOpen ? "opacity-100" : "opacity-0"
        )}>
          <Building2 className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">CRC-ES</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">Sistema de Mensagens</p>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggle}
          className="h-8 w-8 p-0"
        >
          {isOpen ? (
            <ChevronLeft className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-2">
          {filteredNavigation.map((item) => {
            const isActive = location.pathname === item.href
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700",
                  !isOpen && "justify-center"
                )}
              >
                <item.icon className={cn("h-5 w-5", isOpen && "mr-3")} />
                {isOpen && (
                  <span className="transition-opacity duration-300">
                    {item.name}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>
      </ScrollArea>

      <Separator />

      {/* User section */}
      <div className="p-3 space-y-2">
        <Link
          to="/profile"
          className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200",
            location.pathname === '/profile'
              ? "bg-primary text-primary-foreground"
              : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700",
            !isOpen && "justify-center"
          )}
        >
          <User className={cn("h-5 w-5", isOpen && "mr-3")} />
          {isOpen && (
            <span className="transition-opacity duration-300">
              Perfil
            </span>
          )}
        </Link>

        <Button
          variant="ghost"
          onClick={logout}
          className={cn(
            "w-full justify-start text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400",
            !isOpen && "justify-center px-3"
          )}
        >
          <LogOut className={cn("h-5 w-5", isOpen && "mr-3")} />
          {isOpen && (
            <span className="transition-opacity duration-300">
              Sair
            </span>
          )}
        </Button>
      </div>

      {/* User info */}
      {isOpen && user && (
        <div className="p-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-primary-foreground">
                {user.username?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user.username}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user.email}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

