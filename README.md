# BugBountyPipeline
Early development of a customizable recon/attack pipeline written in python3 + luigi

Note:  Currently, only DigitalOcean templates are written for some tools.. but I am looking into AWS and Google Cloud for possible other providers

Done:
  - have each terraform VM generate its own TLS keys in memory for initial access and provisioners
  - have each terraform VM generate its own terraform state.tf file to avoid duplicate errors causing tool crash
  - add some general tools that can be used local or remote
  
TODO:
  - save terraform state files to their own directory instead of top-level
  - write some retry 'wget' logic in the remote-exec provisioners (when used) [to avoid missing a download]
  - see about passing memory TLS keys to luigi contrib for ssh context usage 
   
