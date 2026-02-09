import React, { useState, useRef, useEffect } from 'react';
import { Search, ChevronDown, Check } from 'lucide-react';

interface Option {
    id: number | string;
    label: string;
    subLabel?: string;
    value: any;
}

interface SearchableSelectProps {
    options: Option[];
    placeholder?: string;
    onSelect: (value: any) => void;
    defaultValue?: any;
    className?: string;
}

export default function SearchableSelect({
    options,
    placeholder = 'Seleccionar...',
    onSelect,
    defaultValue,
    className = '',
}: SearchableSelectProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedOption, setSelectedOption] = useState<Option | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (defaultValue !== undefined) {
            const option = options.find((o) => o.id === defaultValue || o.value === defaultValue);
            if (option) setSelectedOption(option);
        }
    }, [defaultValue, options]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const filteredOptions = options.filter(
        (option) =>
            option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (option.subLabel && option.subLabel.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const handleSelect = (option: Option) => {
        setSelectedOption(option);
        setIsOpen(false);
        setSearchTerm('');
        onSelect(option.value);
    };

    return (
        <div className={`relative ${className}`} ref={containerRef}>
            <div
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between px-4 py-2 border border-gray-300 rounded-lg bg-white cursor-pointer hover:border-primary transition-all focus-within:ring-2 focus-within:ring-primary focus-within:border-transparent"
            >
                <span className={`truncate ${!selectedOption ? 'text-gray-400' : 'text-gray-900'}`}>
                    {selectedOption ? selectedOption.label : placeholder}
                </span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </div>

            {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden flex flex-col max-h-72">
                    <div className="p-2 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
                        <Search className="w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            autoFocus
                            placeholder="Buscar..."
                            className="bg-transparent border-none outline-none text-sm w-full py-1"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="overflow-y-auto flex-1">
                        {filteredOptions.length > 0 ? (
                            filteredOptions.map((option) => (
                                <div
                                    key={option.id}
                                    onClick={() => handleSelect(option)}
                                    className={`px-4 py-2 hover:bg-gray-50 cursor-pointer flex items-center justify-between group ${selectedOption?.id === option.id ? 'bg-primary/10 text-primary' : 'text-gray-700'
                                        }`}
                                >
                                    <div className="flex flex-col">
                                        <span className="font-medium">{option.label}</span>
                                        {option.subLabel && <span className="text-xs text-gray-500">{option.subLabel}</span>}
                                    </div>
                                    {selectedOption?.id === option.id && <Check className="w-4 h-4" />}
                                </div>
                            ))
                        ) : (
                            <div className="px-4 py-3 text-sm text-gray-500 text-center">No se encontraron resultados</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
