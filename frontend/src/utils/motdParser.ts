interface ScheduledEvent {
  day: string;
  time: string;
  event: string;
}

interface ParsedMOTD {
  discordUrl: string | null;
  weekRange?: string;
  schedule: ScheduledEvent[];
  fullMotd: string;
}

export function parseMotd(motd: string): ParsedMOTD {
  const result: ParsedMOTD = {
    discordUrl: null,
    schedule: [],
    fullMotd: motd
  };

  // Extract Discord URL
  const discordMatch = motd.match(/Discord:\s*(https:\/\/discord\.gg\/[a-zA-Z0-9]+)/);
  if (discordMatch) {
    result.discordUrl = discordMatch[1];
  }

  // Extract week range
  const weekMatch = motd.match(/Week \d+\s+(\d{2}\/\d{2}\s*-\s*\d{2}\/\d{2})/);
  if (weekMatch) {
    result.weekRange = weekMatch[1];
  }

  // Extract schedule
  const lines = motd.split('\n');
  let currentDay: string | null = null;

  for (const line of lines) {
    // Check for day headers
    const dayMatch = line.match(/^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{2}\/\d{2})/);
    if (dayMatch) {
      currentDay = dayMatch[1];
      continue;
    }

    // If we have a current day, look for events
    if (currentDay) {
      const eventMatch = line.match(/(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s+(.*)/);
      if (eventMatch) {
        result.schedule.push({
          day: currentDay,
          time: eventMatch[1],
          event: eventMatch[2].trim()
        });
      }
    }
  }

  return result;
}

export function formatTime(time: string): string {
  // Ensure consistent time format
  if (!time.includes('AM') && !time.includes('PM')) {
    // Assume PM for times without AM/PM
    const [hours, minutes] = time.split(':').map(n => n.trim());
    const hour = parseInt(hours);
    if (hour < 12) {
      return `${hour}:${minutes} PM`;
    }
    return time;
  }
  return time;
} 