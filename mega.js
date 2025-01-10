// Define the channel ID you're interested in
const channelId = 'your-channel-id-here'; // Replace with your channel ID

// Fetch the EPG XML from the URL
fetch('https://ext.greektv.app/epg/epg.xml')
  .then(response => response.text()) // Get XML as text
  .then(data => {
    // Parse the XML text into an XML DOM object
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(data, 'text/xml');
    
    // Get all the <programme> elements
    const programmes = xmlDoc.getElementsByTagName('programme');
    
    // Get the current date and time
    const now = new Date();
    
    // Convert the current time into a format to compare with the EPG time
    const currentTime = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
    
    // Loop through all programmes to find the one for the specific channel ID
    for (let i = 0; i < programmes.length; i++) {
      const programme = programmes[i];
      
      // Get the channel ID of the programme
      const channel = programme.getAttribute('channel');
      
      // Check if the channel matches the one we're interested in
      if (channel === channelId) {
        // Get the start time and duration of the program
        const startTime = parseInt(programme.getAttribute('start'));
        const duration = parseInt(programme.getAttribute('duration'));
        
        // If the current time is within the program's start and end time, display the program
        if (currentTime >= startTime && currentTime <= (startTime + duration)) {
          const title = programme.getElementsByTagName('title')[0].textContent;
          const description = programme.getElementsByTagName('desc')[0].textContent;
          
          // Display the current program
          console.log(`Current Program on Channel ${channelId}:`);
          console.log(`Title: ${title}`);
          console.log(`Description: ${description}`);
          
          // You can display it in an HTML element, e.g., a div
          document.getElementById('program').innerHTML = `
            <h2>${title}</h2>
            <p>${description}</p>
          `;
          break; // Exit loop after finding the current program
        }
      }
    }
  })
  .catch(error => {
    console.error('Error fetching EPG:', error);
  });
