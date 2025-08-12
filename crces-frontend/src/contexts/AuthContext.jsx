import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // URL base da API
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

  // Função para fazer requisições autenticadas
  const apiRequest = async (endpoint, options = {}) => {
    const token = localStorage.getItem('token')
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config)
      
      if (response.status === 401) {
        // Token expirado ou inválido
        logout()
        throw new Error('Sessão expirada')
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Erro na requisição')
      }

      return await response.json()
    } catch (error) {
      console.error('Erro na API:', error)
      throw error
    }
  }

  // Função de login
  const login = async (username, password) => {
    try {
      setLoading(true)
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Erro no login')
      }

      const data = await response.json()
      
      // Armazena o token
      localStorage.setItem('token', data.access_token)
      
      // Define o usuário
      setUser(data.user)
      
      console.log('Login realizado com sucesso:', `Bem-vindo, ${data.user.username}!`)

      return data
    } catch (error) {
      console.error('Erro no login:', error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Função de logout
  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    console.log('Logout realizado: Você foi desconectado com sucesso.')
  }

  // Função para verificar se o usuário está autenticado
  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        setLoading(false)
        return
      }

      // Verifica se o token é válido fazendo uma requisição para o perfil
      const userData = await apiRequest('/auth/profile')
      setUser(userData.user)
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error)
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  // Função para atualizar perfil do usuário
  const updateProfile = async (profileData) => {
    try {
      const response = await apiRequest('/users/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      })

      setUser(response.user)
      
      console.log('Perfil atualizado: Suas informações foram atualizadas com sucesso.')

      return response
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error.message)
      throw error
    }
  }

  // Função para alterar senha
  const changePassword = async (currentPassword, newPassword) => {
    try {
      await apiRequest('/users/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      })

      console.log('Senha alterada: Sua senha foi alterada com sucesso.')
    } catch (error) {
      console.error('Erro ao alterar senha:', error.message)
      throw error
    }
  }

  // Verifica autenticação ao carregar a aplicação
  useEffect(() => {
    checkAuth()
  }, [])

  const value = {
    user,
    loading,
    login,
    logout,
    updateProfile,
    changePassword,
    apiRequest,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

