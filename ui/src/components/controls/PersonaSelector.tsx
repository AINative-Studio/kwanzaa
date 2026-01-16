/**
 * PersonaSelector Component
 *
 * Allows users to select between different personas (builder, educator, creator, researcher).
 * Enforces Kujichagulia (Self-Determination) through user control.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { Persona } from '../../types/answer-json';
import { GraduationCap, Code, Palette, Search } from 'lucide-react';

export interface PersonaSelectorProps {
  selected: Persona;
  onChange: (persona: Persona) => void;
  className?: string;
}

const personas: Array<{
  key: Persona;
  label: string;
  icon: React.ReactNode;
  description: string;
}> = [
  {
    key: 'educator',
    label: 'Educator',
    icon: <GraduationCap size={20} />,
    description: 'Clear explanations with educational focus',
  },
  {
    key: 'researcher',
    label: 'Researcher',
    icon: <Search size={20} />,
    description: 'Deep analysis with primary sources',
  },
  {
    key: 'creator',
    label: 'Creator',
    icon: <Palette size={20} />,
    description: 'Creative tools grounded in research',
  },
  {
    key: 'builder',
    label: 'Builder',
    icon: <Code size={20} />,
    description: 'Technical implementation guidance',
  },
];

export const PersonaSelector: React.FC<PersonaSelectorProps> = ({
  selected,
  onChange,
  className,
}) => {
  return (
    <div className={clsx('persona-selector', className)}>
      <label className="block text-sm font-medium text-gray-900 mb-2">
        Choose Your Persona
      </label>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {personas.map((persona) => (
          <button
            key={persona.key}
            onClick={() => onChange(persona.key)}
            className={clsx(
              'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
              selected === persona.key
                ? 'border-blue-600 bg-blue-50 text-blue-900'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            )}
          >
            <div className={clsx(
              selected === persona.key ? 'text-blue-600' : 'text-gray-600'
            )}>
              {persona.icon}
            </div>
            <span className="font-medium text-sm">{persona.label}</span>
            <span className="text-xs text-center text-gray-600">{persona.description}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
