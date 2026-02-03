import { type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  BarChart3, FileText, AlertTriangle, Award, 
  Building2, MapPin, ShoppingCart, Bell, 
  ShieldAlert, FileSpreadsheet 
} from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/licitacoes', label: 'Licitações', icon: FileText },
    { path: '/fornecedores', label: 'Fornecedores', icon: Building2 },
    { path: '/municipios', label: 'Municípios', icon: MapPin },
    { path: '/itens', label: 'Itens/Preços', icon: ShoppingCart },
    { path: '/anomalias', label: 'Anomalias', icon: AlertTriangle },
    { path: '/alertas', label: 'Alertas', icon: Bell },
    { path: '/ceis', label: 'CEIS/CNEP', icon: ShieldAlert },
    { path: '/governanca', label: 'Governança', icon: Award },
    { path: '/relatorios', label: 'Relatórios', icon: FileSpreadsheet },
  ];
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            LAP - Licitações Aparecida Plus
          </h1>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b overflow-x-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    isActive(item.path)
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-white shadow-sm mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            © 2024 LAP - Sistema de Licitações Públicas
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
