import React from 'react';
import { ImageInfo } from '../services/api';

// Emoji map for visual representation of image categories
const CATEGORY_EMOJIS: Record<string, string> = {
    mountain: '🏔️',
    ocean: '🌊',
    forest: '🌲',
    desert: '🏜️',
    city: '🌆',
    space: '🚀',
    underwater: '🐠',
    sunset: '🌅',
    snow: '❄️',
    volcano: '🌋',
    garden: '🌸',
    lighthouse: '🗼',
    bridge: '🌉',
    castle: '🏰',
    waterfall: '💧',
    cave: '🦇',
    island: '🏝️',
    aurora: '🌌',
    canyon: '🏜️',
    meadow: '🌻',
};

// Unique gradient for each image based on category
const CATEGORY_GRADIENTS: Record<string, string> = {
    mountain: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    ocean: 'linear-gradient(135deg, #0093E9 0%, #80D0C7 100%)',
    forest: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    desert: 'linear-gradient(135deg, #F2994A 0%, #F2C94C 100%)',
    city: 'linear-gradient(135deg, #434343 0%, #000000 100%)',
    space: 'linear-gradient(135deg, #0c0c1d 0%, #1a1a4e 50%, #3d1f6d 100%)',
    underwater: 'linear-gradient(135deg, #1CB5E0 0%, #000851 100%)',
    sunset: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    snow: 'linear-gradient(135deg, #E3FDF5 0%, #FFE6FA 100%)',
    volcano: 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)',
    garden: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    lighthouse: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    bridge: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    castle: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    waterfall: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
    cave: 'linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)',
    island: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    aurora: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 50%, #96fbc4 100%)',
    canyon: 'linear-gradient(135deg, #f83600 0%, #f9d423 100%)',
    meadow: 'linear-gradient(135deg, #fddb92 0%, #d1fdff 100%)',
};

interface Props {
    images: ImageInfo[];
    selectedIds: string[];
    onToggle: (id: string) => void;
    maxSelections: number;
    disabled?: boolean;
}

export default function ImageGrid({ images, selectedIds, onToggle, maxSelections, disabled }: Props) {
    const handleClick = (id: string) => {
        if (disabled) return;
        if (selectedIds.includes(id)) {
            onToggle(id);
        } else if (selectedIds.length < maxSelections) {
            onToggle(id);
        }
    };

    return (
        <div role="listbox" aria-label="Image selection grid" aria-multiselectable="true">
            <div className="image-grid">
                {images.map((img) => {
                    const isSelected = selectedIds.includes(img.id);
                    const selectionIndex = selectedIds.indexOf(img.id);
                    const gradient = CATEGORY_GRADIENTS[img.category] || CATEGORY_GRADIENTS.mountain;
                    const emoji = CATEGORY_EMOJIS[img.category] || '🖼️';

                    return (
                        <div
                            key={img.id}
                            className={`image-card card ${isSelected ? 'selected' : ''}`}
                            onClick={() => handleClick(img.id)}
                            role="option"
                            tabIndex={0}
                            aria-label={`${img.label} — ${isSelected ? `Selected, position ${selectionIndex + 1}` : 'Not selected'}`}
                            aria-selected={isSelected}
                            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(img.id); } }}
                        >
                            <div
                                className="image-card-visual"
                                style={{ background: gradient }}
                            >
                                <span style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}>{emoji}</span>
                                <span className="image-card-label">{img.label}</span>
                            </div>
                            {isSelected && (
                                <span className="order-badge">{selectionIndex + 1}</span>
                            )}
                        </div>
                    );
                })}
            </div>
            <p className="image-grid-info">
                Selected <strong>{selectedIds.length}</strong> of <strong>{maxSelections}</strong> —
                {selectedIds.length < maxSelections
                    ? ` Choose ${maxSelections - selectedIds.length} more`
                    : ' ✓ Ready to proceed'}
            </p>
        </div>
    );
}
