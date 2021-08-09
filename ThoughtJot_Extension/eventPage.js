let apiKey;

// Gets API key from chrome storage
function getKey()
{
  chrome.storage.sync.get(["apiKey"], function(data){
    apiKey = data.apiKey;
  });
  return apiKey;
}
apiKey = getKey();
  
// Creates a context menu
chrome.contextMenus.create({
  id: "log",
  title: "Jot!",
  contexts: ["selection"]
});

// Checks for click on context menu
chrome.contextMenus.onClicked.addListener(function(clickData){
  if (clickData.menuItemId == "log" && clickData.selectionText)
  {
    
    // Gets current URL of tab and packages selected information
    chrome.tabs.getSelected(null, function(tab) {
      var tabData = tab.url;
      var data = {text: clickData.selectionText, location: tabData, key: getKey()};
      options = {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      };
      // Sends JSON information to local flask server's log route
      fetch("http://localhost:5000/log", options);
    });

  }
});

