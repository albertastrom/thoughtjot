let apiKey;
var regex = /^[A-Z0-9]+$/

// Validates if a Key follows the correct format
function goodKey(key)
{
  if (typeof(key) !== "string")
  {
    alert(key)
    return false;
  }
  key = key.toUpperCase();
  if (key.length != 6)
  {
    return false;
  }
  if (!regex.test(key))
  {
    return false;
  }
  return true;
}


document.addEventListener('DOMContentLoaded', function(){
 
  // Checks if API key exists and then loads it in from storage 
  chrome.storage.sync.get(['apiKey'], function(data){
    if(data.apiKey == undefined)
    {
      document.querySelector('#codeKey').innerHTML = "None";
    }
    else
    {
      document.querySelector('#codeKey').innerHTML = data.apiKey;
    }
    
  });
  
  // Accepts or rejects submitted key by saving it to memory or asking for a another input
  document.querySelector('form').addEventListener('submit', function(){
    if (goodKey(document.querySelector('#key').value))
    {
      alert("Key was saved successfully!");
      apiKey = document.querySelector('#key').value;
      chrome.storage.sync.set({'apiKey': apiKey.toUpperCase()})
      chrome.runtime.reload();
    }
    else
    {
      alert("Invalid Key! Please resubmit.")
    }
  });
});
