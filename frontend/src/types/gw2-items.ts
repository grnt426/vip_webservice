// Base types and enums
export type GameType = 'Activity' | 'Dungeon' | 'Pve' | 'Pvp' | 'PvpLobby' | 'Wvw';
export type Rarity = 'Junk' | 'Basic' | 'Fine' | 'Masterwork' | 'Rare' | 'Exotic' | 'Ascended' | 'Legendary';

export type ItemFlag = 
  | 'AccountBindOnUse' | 'AccountBound' | 'Attuned' | 'BulkConsume'
  | 'DeleteWarning' | 'HideSuffix' | 'Infused' | 'MonsterOnly'
  | 'NoMysticForge' | 'NoSalvage' | 'NoSell' | 'NotUpgradeable'
  | 'NoUnderwater' | 'SoulbindOnAcquire' | 'SoulBindOnUse'
  | 'Tonic' | 'Unique';

export type Restriction = 
  | 'Asura' | 'Charr' | 'Female' | 'Human' | 'Norn'
  | 'Revenant' | 'Sylvari' | 'Elementalist' | 'Engineer'
  | 'Guardian' | 'Mesmer' | 'Necromancer' | 'Ranger'
  | 'Thief' | 'Warrior';

// Infusion slot interface
export interface InfusionSlot {
  flags: ('Enrichment' | 'Infusion')[];
  item_id?: number;
}

// Infix upgrade interface
export interface AttributeBonus {
  attribute: 
    | 'AgonyResistance' | 'BoonDuration' | 'ConditionDamage'
    | 'ConditionDuration' | 'CritDamage' | 'Healing'
    | 'Power' | 'Precision' | 'Toughness' | 'Vitality';
  modifier: number;
}

export interface InfixUpgrade {
  id?: number;
  attributes: AttributeBonus[];
  buff?: {
    skill_id: number;
    description?: string;
  };
}

// Base item interface
export interface BaseItem {
  id: number;
  chat_link: string;
  name: string;
  icon?: string;
  description?: string;
  type: ItemType;
  level: number;
  rarity: Rarity;
  vendor_value: number;
  default_skin?: number;
  flags: ItemFlag[];
  game_types: GameType[];
  restrictions: Restriction[];
  upgrades_into?: {
    upgrade: 'Attunement' | 'Infusion';
    item_id: number;
  }[];
  upgrades_from?: {
    upgrade: 'Attunement' | 'Infusion';
    item_id: number;
  }[];
}

// Type-specific interfaces
export interface ArmorDetails {
  type: 'Boots' | 'Coat' | 'Gloves' | 'Helm' | 'HelmAquatic' | 'Leggings' | 'Shoulders';
  weight_class: 'Heavy' | 'Medium' | 'Light' | 'Clothing';
  defense: number;
  infusion_slots: InfusionSlot[];
  attribute_adjustment: number;
  infix_upgrade?: InfixUpgrade;
  suffix_item_id?: number;
  secondary_suffix_item_id: string;
  stat_choices?: number[];
}

export interface BackItemDetails {
  infusion_slots: InfusionSlot[];
  attribute_adjustment: number;
  infix_upgrade?: InfixUpgrade;
  suffix_item_id?: number;
  secondary_suffix_item_id: string;
  stat_choices?: number[];
}

export interface BagDetails {
  size: number;
  no_sell_or_sort: boolean;
}

export interface ConsumableDetails {
  type: 'AppearanceChange' | 'Booze' | 'ContractNpc' | 'Currency' | 'Food' 
    | 'Generic' | 'Halloween' | 'Immediate' | 'MountRandomUnlock' | 'RandomUnlock'
    | 'Transmutation' | 'Unlock' | 'UpgradeRemoval' | 'Utility' | 'TeleportToFriend';
  description?: string;
  duration_ms?: number;
  unlock_type?: string;
  color_id?: number;
  recipe_id?: number;
  extra_recipe_ids?: number[];
  guild_upgrade_id?: number;
  apply_count?: number;
  name?: string;
  icon?: string;
  skins?: number[];
}

export interface ContainerDetails {
  type: 'Default' | 'GiftBox' | 'Immediate' | 'OpenUI';
}

export interface GatheringDetails {
  type: 'Foraging' | 'Logging' | 'Mining' | 'Bait' | 'Lure';
}

export interface GizmoDetails {
  type: 'Default' | 'ContainerKey' | 'RentableContractNpc' | 'UnlimitedConsumable';
  guild_upgrade_id?: number;
  vendor_ids?: number[];
}

export interface MiniPetDetails {
  minipet_id: number;
}

export interface SalvageKitDetails {
  type: 'Salvage';
  charges: number;
}

export interface TrinketDetails {
  type: 'Accessory' | 'Amulet' | 'Ring';
  infusion_slots: InfusionSlot[];
  attribute_adjustment: number;
  infix_upgrade?: InfixUpgrade;
  suffix_item_id?: number;
  secondary_suffix_item_id: string;
  stat_choices?: number[];
}

export interface UpgradeComponentDetails {
  type: 'Default' | 'Gem' | 'Rune' | 'Sigil';
  flags: string[];
  infusion_upgrade_flags: ('Enrichment' | 'Infusion')[];
  suffix: string;
  infix_upgrade: InfixUpgrade;
  bonuses?: string[];
}

export interface WeaponDetails {
  type: string; // Too many to enumerate
  damage_type: 'Fire' | 'Ice' | 'Lightning' | 'Physical' | 'Choking';
  min_power: number;
  max_power: number;
  defense: number;
  infusion_slots: InfusionSlot[];
  attribute_adjustment: number;
  infix_upgrade?: InfixUpgrade;
  suffix_item_id?: number;
  secondary_suffix_item_id: string;
  stat_choices?: number[];
}

// Union type for all possible item types
export type ItemType = 
  | 'Armor' | 'Back' | 'Bag' | 'Consumable' | 'Container' 
  | 'CraftingMaterial' | 'Gathering' | 'Gizmo' | 'JadeTechModule'
  | 'Key' | 'MiniPet' | 'PowerCore' | 'Relic' | 'Tool'
  | 'Trait' | 'Trinket' | 'Trophy' | 'UpgradeComponent' | 'Weapon';

// Complete item interfaces
export interface ArmorItem extends BaseItem {
  type: 'Armor';
  details: ArmorDetails;
}

export interface BackItem extends BaseItem {
  type: 'Back';
  details: BackItemDetails;
}

export interface BagItem extends BaseItem {
  type: 'Bag';
  details: BagDetails;
}

export interface ConsumableItem extends BaseItem {
  type: 'Consumable';
  details: ConsumableDetails;
}

export interface ContainerItem extends BaseItem {
  type: 'Container';
  details: ContainerDetails;
}

export interface GatheringItem extends BaseItem {
  type: 'Gathering';
  details: GatheringDetails;
}

export interface GizmoItem extends BaseItem {
  type: 'Gizmo';
  details: GizmoDetails;
}

export interface MiniPetItem extends BaseItem {
  type: 'MiniPet';
  details: MiniPetDetails;
}

export interface SalvageKitItem extends BaseItem {
  type: 'Tool';
  details: SalvageKitDetails;
}

export interface TrinketItem extends BaseItem {
  type: 'Trinket';
  details: TrinketDetails;
}

export interface UpgradeComponentItem extends BaseItem {
  type: 'UpgradeComponent';
  details: UpgradeComponentDetails;
}

export interface WeaponItem extends BaseItem {
  type: 'Weapon';
  details: WeaponDetails;
}

// Simple items without details
export interface SimpleItem extends BaseItem {
  type: 'CraftingMaterial' | 'JadeTechModule' | 'Key' | 'PowerCore' | 'Relic' | 'Trait' | 'Trophy';
}

// Union type for all possible items
export type GW2Item = 
  | ArmorItem | BackItem | BagItem | ConsumableItem 
  | ContainerItem | GatheringItem | GizmoItem | MiniPetItem 
  | SalvageKitItem | TrinketItem | UpgradeComponentItem 
  | WeaponItem | SimpleItem;

export type GW2ItemRarity = 'Junk' | 'Basic' | 'Fine' | 'Masterwork' | 'Rare' | 'Exotic' | 'Ascended' | 'Legendary'; 