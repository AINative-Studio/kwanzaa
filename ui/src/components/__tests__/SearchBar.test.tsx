import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchBar } from '../SearchBar';

describe('SearchBar', () => {
  it('renders with placeholder text', () => {
    render(
      <SearchBar
        value=""
        onChange={vi.fn()}
        onSearch={vi.fn()}
      />
    );

    expect(screen.getByPlaceholderText(/search the kwanzaa corpus/i)).toBeInTheDocument();
  });

  it('calls onChange when typing', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <SearchBar
        value=""
        onChange={onChange}
        onSearch={vi.fn()}
      />
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'test query');

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled();
    });
  });

  it('calls onSearch when form is submitted', async () => {
    const onSearch = vi.fn();
    const user = userEvent.setup();

    render(
      <SearchBar
        value="test query"
        onChange={vi.fn()}
        onSearch={onSearch}
      />
    );

    const button = screen.getByRole('button', { name: /search/i });
    await user.click(button);

    expect(onSearch).toHaveBeenCalledTimes(1);
  });

  it('disables search button when query is empty', () => {
    render(
      <SearchBar
        value=""
        onChange={vi.fn()}
        onSearch={vi.fn()}
      />
    );

    const button = screen.getByRole('button', { name: /search/i });
    expect(button).toBeDisabled();
  });

  it('shows loading state when searching', () => {
    render(
      <SearchBar
        value="test"
        onChange={vi.fn()}
        onSearch={vi.fn()}
        isSearching={true}
      />
    );

    expect(screen.getByText(/searching/i)).toBeInTheDocument();
  });

  it('shows clear button when value is not empty', () => {
    render(
      <SearchBar
        value="test query"
        onChange={vi.fn()}
        onSearch={vi.fn()}
      />
    );

    expect(screen.getByLabelText(/clear search/i)).toBeInTheDocument();
  });

  it('clears input when clear button is clicked', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <SearchBar
        value="test query"
        onChange={onChange}
        onSearch={vi.fn()}
      />
    );

    const clearButton = screen.getByLabelText(/clear search/i);
    await user.click(clearButton);

    expect(onChange).toHaveBeenCalledWith('');
  });
});
