import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Licitacoes from './pages/Licitacoes';
import Fornecedores from './pages/Fornecedores';
import Municipios from './pages/Municipios';
import Itens from './pages/Itens';
import Anomalias from './pages/Anomalias';
import Alertas from './pages/Alertas';
import CEIS from './pages/CEIS';
import Governanca from './pages/Governanca';
import Relatorios from './pages/Relatorios';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/licitacoes" element={<Licitacoes />} />
            <Route path="/fornecedores" element={<Fornecedores />} />
            <Route path="/municipios" element={<Municipios />} />
            <Route path="/itens" element={<Itens />} />
            <Route path="/anomalias" element={<Anomalias />} />
            <Route path="/alertas" element={<Alertas />} />
            <Route path="/ceis" element={<CEIS />} />
            <Route path="/governanca" element={<Governanca />} />
            <Route path="/relatorios" element={<Relatorios />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
