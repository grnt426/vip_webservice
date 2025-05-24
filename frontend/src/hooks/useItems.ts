import { useState, useCallback } from 'react';
import { GW2Item } from '../types/gw2-items';
import ItemService from '../services/ItemService';

interface UseItemsResult {
  getItem: (id: number) => Promise<GW2Item>;
  getItems: (ids: number[]) => Promise<GW2Item[]>;
  searchItems: (query: string) => Promise<GW2Item[]>;
  isLoading: boolean;
  error: Error | null;
}

export function useItems(): UseItemsResult {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const itemService = ItemService.getInstance();

  const handleRequest = useCallback(async <T>(request: () => Promise<T>): Promise<T> => {
    setError(null);
    setIsLoading(true);
    try {
      const result = await request();
      return result;
    } catch (e) {
      const error = e instanceof Error ? e : new Error('An unknown error occurred');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [setIsLoading, setError]);

  const getItem = useCallback(async (id: number): Promise<GW2Item> => {
    return handleRequest(() => itemService.getItem(id));
  }, [itemService, handleRequest]);

  const getItems = useCallback(async (ids: number[]): Promise<GW2Item[]> => {
    return handleRequest(() => itemService.getItems(ids));
  }, [itemService, handleRequest]);

  const searchItems = useCallback(async (query: string): Promise<GW2Item[]> => {
    return handleRequest(() => itemService.searchItems(query));
  }, [itemService, handleRequest]);

  return {
    getItem,
    getItems,
    searchItems,
    isLoading,
    error,
  };
}

// Example usage:
/*
function MyComponent() {
  const { getItem, isLoading, error } = useItems();
  const [item, setItem] = useState<GW2Item | null>(null);

  useEffect(() => {
    getItem(12452) // Fetch Omnomberry Bar
      .then(setItem)
      .catch(console.error);
  }, [getItem]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!item) return null;

  return <ItemDisplay item={item} />;
}
*/ 