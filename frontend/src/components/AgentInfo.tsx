import React from 'react';
import type { AgentInfo as AgentInfoType } from '../types';

interface AgentInfoProps {
  info: AgentInfoType;
}

const AgentInfo: React.FC<AgentInfoProps> = ({ info }) => {
  return (
    <div className="mt-4 pt-4" style={{ borderTopColor: '#B6B09F' }}>
      <div className="flex items-center mb-3">
        <h4 className="text-sm font-semibold" style={{ color: '#000000' }}>Agent Info</h4>
      </div>
      
      <div className="space-y-2 text-xs">
        <div className="flex items-center justify-between p-2 rounded-md" style={{ backgroundColor: '#EAE4D5' }}>
          <span className="font-medium" style={{ color: '#B6B09F' }}>Name:</span>
          <span className="font-semibold" style={{ color: '#000000' }}>{info.name}</span>
        </div>
        
        <div className="flex items-center justify-between p-2 rounded-md" style={{ backgroundColor: '#EAE4D5' }}>
          <span className="font-medium" style={{ color: '#B6B09F' }}>Products:</span>
          <span className="font-semibold" style={{ color: '#000000' }}>{info.total_products}</span>
        </div>
        
        <div>
          <span className="font-medium mb-1 block" style={{ color: '#B6B09F' }}>Capabilities:</span>
          <div className="space-y-1">
            {info.capabilities.map((capability, index) => (
              <div key={index} className="flex items-center space-x-1 p-1 rounded" style={{ backgroundColor: '#EAE4D5' }}>
                <span style={{ color: '#000000' }}>{capability}</span>
              </div>
            ))}
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default AgentInfo;