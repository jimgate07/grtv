  // Function to fetch and parse the XML file
  async function fetchEPGData() {
    try {
      const response = await fetch('https://raw.githubusercontent.com/possiblelife/gtrvlst/refs/heads/main/grgu.xml');
      const text = await response.text();
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(text, 'application/xml');
      
      // Define the channel you want to check for. Adjust this to your channel.
      const channelId = 'Mega'; // Change this to the specific channel ID you want to check
      const channel = xmlDoc.querySelector(`channel[id="${channelId}"]`);

      if (channel) {
        // Get the live program and next program
        const currentProgram = getCurrentProgram(xmlDoc, channelId);
        const nextProgram = getNextProgram(xmlDoc, channelId);

        // Display the results on the website
        document.getElementById('current-program').innerText = currentProgram;
        document.getElementById('next-program-name').innerText = nextProgram;
      } else {
        console.error('Channel not found!');
      }
    } catch (error) {
      console.error('Error fetching or parsing XML:', error);
    }
  }

  // Function to get the current time in the required format: YYYYMMDDHHMMSS +TZ
  function getCurrentTimeFormatted() {
    const now = new Date();
    const offset = now.getTimezoneOffset();
    const offsetHours = Math.floor(Math.abs(offset) / 60);
    const offsetMinutes = Math.abs(offset) % 60;
    const offsetSign = offset > 0 ? '-' : '+';
    const offsetString = `${offsetSign}${String(offsetHours).padStart(2, '0')}${String(offsetMinutes).padStart(2, '0')}`;

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    const second = String(now.getSeconds()).padStart(2, '0');

    return `${year}${month}${day}${hour}${minute}${second} ${offsetString}`;
  }

  // Function to find the current program for the specified channel
  function getCurrentProgram(xmlDoc, channelId) {
    const currentTime = getCurrentTimeFormatted();
    const programs = xmlDoc.querySelectorAll(`programme[channel="${channelId}"]`);
    
    for (let program of programs) {
      const startTime = formatXMLTimeToISO(program.getAttribute('start'));
      const endTime = formatXMLTimeToISO(program.getAttribute('stop'));
      
      if (startTime <= currentTime && endTime >= currentTime) {
        return program.querySelector('title').textContent;
      }
    }

    return 'No program currently playing';
  }

  // Function to find the next program for the specified channel
  function getNextProgram(xmlDoc, channelId) {
    const currentTime = getCurrentTimeFormatted();
    const programs = xmlDoc.querySelectorAll(`programme[channel="${channelId}"]`);
    
    for (let program of programs) {
      const startTime = formatXMLTimeToISO(program.getAttribute('start'));
      
      if (startTime > currentTime) {
        return program.querySelector('title').textContent;
      }
    }

    return 'No upcoming program';
  }

  // Function to format XML time to comparable format YYYYMMDDHHMMSS +TZ
  function formatXMLTimeToISO(xmlTime) {
    const year = xmlTime.substring(0, 4);
    const month = xmlTime.substring(4, 6);
    const day = xmlTime.substring(6, 8);
    const hour = xmlTime.substring(8, 10);
    const minute = xmlTime.substring(10, 12);
    const second = xmlTime.substring(12, 14);
    const timezone = xmlTime.substring(14);

    return `${year}${month}${day}${hour}${minute}${second} ${timezone}`;
  }

  // Fetch the EPG data when the page loads
  window.onload = function() {
    fetchEPGData();
  };