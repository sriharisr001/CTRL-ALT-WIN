import { createContext, useContext, useState } from 'react'
import { readApiResponse } from '../api'
const Auth = createContext()
export const useAuth = () => useContext(Auth)
export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('satyafin_token'))
  const authenticate = async (mode, credentials) => {
    const response = await fetch(`/api/auth/${mode}`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(credentials) })
    const data = await readApiResponse(response)
    localStorage.setItem('satyafin_token', data.access_token); setToken(data.access_token)
  }
  const logout = () => { localStorage.removeItem('satyafin_token'); setToken(null) }
  return <Auth.Provider value={{token, authenticate, logout}}>{children}</Auth.Provider>
}
