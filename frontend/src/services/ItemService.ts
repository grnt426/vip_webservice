import { GW2Item } from '../types/gw2-items';

class ItemService {
  private static instance: ItemService;

  private constructor() {}

  public static getInstance(): ItemService {
    if (!ItemService.instance) {
      ItemService.instance = new ItemService();
    }
    return ItemService.instance;
  }

  public async getItem(id: number): Promise<GW2Item> {
    const response = await fetch(`/api/items/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch item ${id}`);
    }
    return response.json();
  }

  public async getItems(ids: number[]): Promise<GW2Item[]> {
    // Deduplicate IDs
    const uniqueIds = [...new Set(ids)];
    
    // Split into batches of 200 (API limit)
    const batchSize = 200;
    const batches: number[][] = [];
    
    for (let i = 0; i < uniqueIds.length; i += batchSize) {
      batches.push(uniqueIds.slice(i, i + batchSize));
    }

    const batchResults = await Promise.all(
      batches.map(async batch => {
        const params = new URLSearchParams();
        params.set('ids', batch.join(','));
        
        const response = await fetch(`/api/items?${params}`);
        if (!response.ok) {
          throw new Error('Failed to fetch items batch');
        }
        
        return response.json();
      })
    );

    return batchResults.flat();
  }

  public async searchItems(query: string): Promise<GW2Item[]> {
    const params = new URLSearchParams({
      query: query,
      limit: '50' // Limit results to 50 items
    });
    
    const response = await fetch(`/api/items/search?${params}`);
    if (!response.ok) {
      throw new Error('Failed to search items');
    }

    return response.json();
  }
}

export default ItemService; 