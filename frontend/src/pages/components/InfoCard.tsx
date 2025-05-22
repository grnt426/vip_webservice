import { Card, CardContent, Typography } from '@mui/material';

interface InfoCardProps {
  title: string;
  description: string;
  footer?: string;
}

const InfoCard: React.FC<InfoCardProps> = ({ title, description, footer }) => {
  return (
    <Card sx={{ maxWidth: 400, m: 2, boxShadow: 3 }}>
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
        {footer && (
          <Typography variant="caption" display="block" sx={{ mt: 2, color: 'text.disabled' }}>
            {footer}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default InfoCard;
