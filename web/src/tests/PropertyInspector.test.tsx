import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PropertyInspector } from '../components/Inspector/PropertyInspector';
import type { CatalogExerciseItem, ExerciseBlockSpec } from '../types/models';

const mockCatalog: CatalogExerciseItem[] = [
  {
    type: 'zahlenmauer',
    name: 'Zahlenmauer',
    category: 'Arithmetic Puzzles',
    description: 'Addition pyramid',
    default_width: 70,
    default_height: 45,
    default_params: { base_size: 4, difficulty: 'medium' },
    params: [
      {
        name: 'base_size',
        label: 'Base Size (Steine)',
        type: 'int',
        default: 4,
        min: 3,
        max: 8,
      },
      {
        name: 'difficulty',
        label: 'Difficulty',
        type: 'select',
        default: 'medium',
        options: ['easy', 'medium', 'hard'],
      },
    ],
  },
];

describe('PropertyInspector Component', () => {
  it('renders sheet global settings when no block is selected', () => {
    const onUpdateHeader = vi.fn();
    render(
      <PropertyInspector
        selectedBlock={null}
        catalog={mockCatalog}
        header={{
          title: 'Test Blatt',
          subtitle: 'Klasse 2',
          show_date_field: true,
          show_name_field: true,
        }}
        onUpdateHeader={onUpdateHeader}
        onUpdateBlock={vi.fn()}
        onUpdateParams={vi.fn()}
        onDeleteBlock={vi.fn()}
        onDuplicateBlock={vi.fn()}
      />
    );

    expect(screen.getByText('Blatt-Eigenschaften')).toBeInTheDocument();
    const titleInput = screen.getByDisplayValue('Test Blatt');
    expect(titleInput).toBeInTheDocument();

    fireEvent.change(titleInput, { target: { value: 'Neuer Titel' } });
    expect(onUpdateHeader).toHaveBeenCalledWith({ title: 'Neuer Titel' });
  });

  it('renders dynamic parameter inputs when block is selected', () => {
    const onUpdateParams = vi.fn();
    const selectedBlock: ExerciseBlockSpec = {
      id: 'block-1',
      type: 'zahlenmauer',
      x: 20,
      y: 40,
      width: 70,
      height: 45,
      scale: 1.0,
      params: { base_size: 4, difficulty: 'medium' },
    };

    render(
      <PropertyInspector
        selectedBlock={selectedBlock}
        catalog={mockCatalog}
        header={{
          title: 'Blatt',
          subtitle: '',
          show_date_field: true,
          show_name_field: true,
        }}
        onUpdateHeader={vi.fn()}
        onUpdateBlock={vi.fn()}
        onUpdateParams={onUpdateParams}
        onDeleteBlock={vi.fn()}
        onDuplicateBlock={vi.fn()}
      />
    );

    expect(screen.getByText('Zahlenmauer')).toBeInTheDocument();
    expect(screen.getByText('Base Size (Steine)')).toBeInTheDocument();

    const difficultySelect = screen.getByDisplayValue('medium');
    fireEvent.change(difficultySelect, { target: { value: 'hard' } });
    expect(onUpdateParams).toHaveBeenCalledWith('block-1', { difficulty: 'hard' });
  });
});
