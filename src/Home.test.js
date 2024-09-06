import { render, screen } from '@testing-library/react';
import Home from '../index';

test('renders Home component with text "Home world"', () => {
  render(<Home />);
  const linkElement = screen.getByText(/Home world/i);
  expect(linkElement).toBeInTheDocument();
});
