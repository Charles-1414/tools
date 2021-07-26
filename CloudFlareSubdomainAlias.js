/** 
 * This is a javascript that runs on CloudFlare worker
 * It will work as a domain alias redirector.
 * It's hard to explain that, so below is an example:
 * My main domain is charles14.xyz, and I have a shorter domain (alias) cw14.xyz
 * This script will forward all traffic to *.cw14.xyz/* to *.charles14.xyz/*
 * 
 * This works nice if your Virtual Hosts are binded to the main domain which do not accept alias (If you are directly adding a CNAME record). 
 * Because it may take some time to add another Virtual Host for alias.
 * 
 * Note: This script only works for "subdomains" (including 'www'), which means the root domain (@) need to be configured separately.
*/

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
  })
  
  /**
   * Respond to the request
   * @param {Request} request
   */
  async function handleRequest(request) {
    const domain="cw14.xyz"; // *** change this to your alias domain
    var url=request.url;
    var subdomain=url.substr(url.indexOf("/")+2,url.indexOf(domain)-url.indexOf("/")-3);
    var path=url.substr(url.indexOf(domain)+domain.length,url.length-domain.length-url.indexOf(domain));
    const destdomain="charles14.xyz"; // *** change this to your main domain
    var desturl="http://"+subdomain+"."+destdomain+path;
    if(subdomain==""){//root
      desturl="http://"+destdomain+path;
    }
    return Response.redirect(desturl, 301);
  }