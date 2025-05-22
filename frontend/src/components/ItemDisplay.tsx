import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  Divider,
  Skeleton,
} from '@mui/material';
import { GW2Item } from '../types/gw2-items';

interface ItemDisplayProps {
  item?: GW2Item;
  isLoading?: boolean;
  showDetails?: boolean;
}

const RarityColors = {
  Junk: '#AAA',
  Basic: '#000',
  Fine: '#62A4DA',
  Masterwork: '#1a9306',
  Rare: '#fcd00b',
  Exotic: '#ffa405',
  Ascended: '#fb3e8d',
  Legendary: '#4C139D',
};

const formatDuration = (ms: number): string => {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
};

const ItemDisplay: React.FC<ItemDisplayProps> = ({ item, isLoading = false, showDetails = true }) => {
  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="text" />
          <Skeleton variant="text" />
        </CardContent>
      </Card>
    );
  }

  if (!item) {
    return null;
  }

  const renderFlags = () => (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
      {item.flags.map((flag) => (
        <Chip
          key={flag}
          label={flag}
          size="small"
          sx={{ fontSize: '0.7rem' }}
        />
      ))}
    </Box>
  );

  const renderAttributes = (attributes: { attribute: string; modifier: number }[]) => (
    <Box sx={{ mt: 1 }}>
      {attributes.map((attr, index) => (
        <Typography key={index} variant="body2" color="text.secondary">
          {attr.attribute}: +{attr.modifier}
        </Typography>
      ))}
    </Box>
  );

  const renderConsumableDetails = () => {
    if (item.type !== 'Consumable' || !item.details) return null;
    const details = item.details;

    return (
      <Box sx={{ mt: 1 }}>
        {details.duration_ms && (
          <Typography variant="body2">
            Duration: {formatDuration(details.duration_ms)}
          </Typography>
        )}
        {details.description && (
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {details.description}
          </Typography>
        )}
      </Box>
    );
  };

  const renderWeaponDetails = () => {
    if (item.type !== 'Weapon' || !item.details) return null;
    const details = item.details;

    return (
      <Box sx={{ mt: 1 }}>
        <Typography variant="body2">
          Damage: {details.min_power} - {details.max_power} ({details.damage_type})
        </Typography>
        {details.defense > 0 && (
          <Typography variant="body2">
            Defense: {details.defense}
          </Typography>
        )}
        {details.infix_upgrade?.attributes && renderAttributes(details.infix_upgrade.attributes)}
      </Box>
    );
  };

  const renderArmorDetails = () => {
    if (item.type !== 'Armor' || !item.details) return null;
    const details = item.details;

    return (
      <Box sx={{ mt: 1 }}>
        <Typography variant="body2">
          Defense: {details.defense}
        </Typography>
        <Typography variant="body2">
          Weight: {details.weight_class}
        </Typography>
        {details.infix_upgrade?.attributes && renderAttributes(details.infix_upgrade.attributes)}
      </Box>
    );
  };

  const renderUpgradeComponentDetails = () => {
    if (item.type !== 'UpgradeComponent' || !item.details) return null;
    const details = item.details;

    return (
      <Box sx={{ mt: 1 }}>
        {details.bonuses && (
          <Box>
            <Typography variant="body2" fontWeight="bold">Bonuses:</Typography>
            {details.bonuses.map((bonus, index) => (
              <Typography key={index} variant="body2">
                ({index + 1}): {bonus}
              </Typography>
            ))}
          </Box>
        )}
        {details.infix_upgrade?.attributes && renderAttributes(details.infix_upgrade.attributes)}
      </Box>
    );
  };

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2}>
          {item.icon && (
            <Grid sx={{ display: 'flex' }}>
              <img 
                src={item.icon} 
                alt={item.name}
                style={{ width: 32, height: 32 }}
              />
            </Grid>
          )}
          <Grid sx={{ flex: 1 }}>
            <Typography 
              variant="h6" 
              component="div"
              sx={{ 
                color: RarityColors[item.rarity],
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
            >
              {item.name}
              <Chip 
                label={item.type} 
                size="small"
                sx={{ ml: 1 }}
              />
            </Typography>
            
            {item.description && (
              <Typography variant="body2" color="text.secondary">
                {item.description}
              </Typography>
            )}

            {showDetails && (
              <>
                <Divider sx={{ my: 1 }} />
                
                <Typography variant="body2">
                  Level {item.level} {item.rarity}
                </Typography>

                {item.vendor_value > 0 && (
                  <Typography variant="body2">
                    Vendor value: {item.vendor_value} copper
                  </Typography>
                )}

                {renderConsumableDetails()}
                {renderWeaponDetails()}
                {renderArmorDetails()}
                {renderUpgradeComponentDetails()}

                {renderFlags()}
              </>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ItemDisplay; 