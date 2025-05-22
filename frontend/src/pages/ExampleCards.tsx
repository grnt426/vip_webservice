import { Box } from '@mui/material';

import InfoCard from './components/InfoCard';

// This will eventually be fetched from the back end.
const someData = [
  {
    title: 'VIP Guild',
    description: 'VIP Guild',
    footer: 'Insert footer here'
  },
  {
    title: 'John Doe',
    description: 'A person',
  },
  {
    title: "User Signups",
    description: "234 new users today.",
    footer: "Data as of 4 PM",
  },
]

const ExampleCardsPage: React.FC = () => {
  return (
    <Box display='flex' flexWrap='wrap'>
      {someData.map((item, index) => (
        <InfoCard
          key={index}
          title={item.title}
          description={item.description}
          footer={item.footer}
        />
        ))
      }
    </Box>

  )
  };

export default ExampleCardsPage;