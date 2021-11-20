import '../App.css';
import React, { useEffect, useState } from "react";
import url from './server_api_url.txt';
import update_url from './update_api_url.txt';
import axios from "axios";

function Report({auth_url_json}) {

    const [token, setToken] = useState("")
    const [is_error, setError] = useState(false)
    const [responseCode, setResponseCode] = useState(0)

    const [repoURL, setURL] = useState(auth_url_json['code'])

    console.log('passed correctly!')
    console.log(auth_url_json)

    // Check whether user is authenticated or not and if they are return list of secrets to be displayed
    const [secrets, setSecrets] = useState([])
    useEffect(() => {
      const getData = () => {
         fetch(url) // Fetch Lambda url to request from  
          .then(r => r.text()) 
          .then(async text => {
            try {
              
              // Send code + repo_url as a post request to server
              const body = {code : auth_url_json['code'], repo_url : auth_url_json['repo_url']};
              const headers = { 
                "Content-Type": "application/json"
              };
              //TODO: change url back to text.concat("/") in live
              let result = await axios.post(text.concat("/"), body, headers);
              console.log(result);
              
              const secret_list = (result.data)['secrets'];
              setSecrets(JSON.parse(secret_list))
              console.log(secret_list)

              const token_data = (result.data)['token'];

              setToken(token_data);
              console.log(token_data)
              setURL(auth_url_json['repo_url']);

              setResponseCode(1)

            } catch (error) {
              console.log(error);
              setError(true);
            }
      });
      };
      getData();
    }, []);  
    
    // Send secret code review report back to backend lambda 
    const sendForm = (event) => {
      const formData = new FormData(event.currentTarget);
      event.preventDefault();
      console.log(Array.from(formData.entries()))
      fetch(update_url).then(r => r.text()).then(text => { //Fetch the API url

        const body = { body: Array.from(formData.entries()), repo_url : repoURL, token : token};
        console.log(body)
        const headers = { 
            "Content-Type": "application/json"
        };
        const result =  axios.post(text.concat("/"), body, { headers }) //TODO: change to text.concat("/") when live
        alert("Report Submitted!");
        
      });
    }

    if (is_error == true) {
      return(<div><p> Authentication Error Occured. </p> <a href={"https://github.com/".concat(auth_url_json['repo_url'])}> Return to Github </a>  </div>);
    }
    else if (responseCode == 0) {
      return(<p>Loading</p>);
    }
    else {
      return (
      <div>
        <form onSubmit={(event) => sendForm(event)}>
  
          <h2> Secrets Report</h2>
          <input type="hidden" name="id" value={repoURL}/>
  
          <p>Secrets report</p>
          
          {secrets.map(secret => (
          <div>
          <h2>{secret.id}. {secret.type} found in {secret.location}</h2>
          <a> {secret.code_location} </a>
          <ul>
              <p><input type="radio" value="hub" name={secret.id} required></input> To Hub </p>
              <p><input type="radio" value="allow" name={secret.id} required></input> To Allow </p>
          </ul>
          </div>
          ))}
  
          <p>*All boxes must be selected to send</p>
          
          <button type="submit"> Submit </button>
          </form>
      </div>
    );
  }
}
  
  export default Report;
  