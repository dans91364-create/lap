import { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Municipio {
  id: number;
  nome: string;
  latitude: number;
  longitude: number;
  total_licitacoes?: number;
  valor_total?: number;
}

interface MunicipiosMapProps {
  municipios: Municipio[];
  center?: [number, number];
  zoom?: number;
  height?: string;
}

const MunicipiosMap = ({ 
  municipios, 
  center = [-16.6869, -49.2648], // Goiânia
  zoom = 8,
  height = '600px'
}: MunicipiosMapProps) => {
  useEffect(() => {
    // Fix leaflet icon issue with React
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    });
  }, []);

  const getColor = (valor: number) => {
    if (valor < 1000000) return '#10b981'; // green < 1M
    if (valor < 10000000) return '#f59e0b'; // yellow 1-10M
    return '#ef4444'; // red > 10M
  };

  const getRadius = (totalLicitacoes: number) => {
    return Math.min(Math.max(totalLicitacoes / 2, 5), 30);
  };

  return (
    <div style={{ height }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {municipios.map((municipio) => (
          <CircleMarker
            key={municipio.id}
            center={[municipio.latitude, municipio.longitude]}
            radius={getRadius(municipio.total_licitacoes || 0)}
            fillColor={getColor(municipio.valor_total || 0)}
            color="#fff"
            weight={2}
            opacity={1}
            fillOpacity={0.6}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-bold text-lg">{municipio.nome}</h3>
                <p className="text-sm">
                  <strong>Licitações:</strong> {municipio.total_licitacoes || 0}
                </p>
                <p className="text-sm">
                  <strong>Valor Total:</strong> R$ {(municipio.valor_total || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MunicipiosMap;
