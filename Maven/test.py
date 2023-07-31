import requests as rq
from bs4 import BeautifulSoup
from bs4.element import NavigableString


maven = """
<!DOCTYPE html>
<html>

<head>
	<title>Central Repository: avalon-logging</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<style>
body {
	background: #fff;
}
	</style>
</head>

<body>
	<header>
		<h1>avalon-logging</h1>
	</header>
	<hr/>
	<main>
		<pre id="contents">
<a href="../">../</a>
<a href="avalon-log4j-impl/" title="avalon-log4j-impl/">avalon-log4j-impl/</a>                                               -         -      
<a href="avalon-logging-api/" title="avalon-logging-api/">avalon-logging-api/</a>                                              -         -      
<a href="avalon-logging-impl/" title="avalon-logging-impl/">avalon-logging-impl/</a>                                             -         -      
<a href="avalon-logging-log4j/" title="avalon-logging-log4j/">avalon-logging-log4j/</a>                                            -         -      
<a href="avalon-logging-logkit-api/" title="avalon-logging-logkit-api/">avalon-logging-logkit-api/</a>                                       -         -      
<a href="avalon-logging-logkit-datagram/" title="avalon-logging-logkit-datagram/">avalon-logging-logkit-datagram/</a>                                  -         -      
<a href="avalon-logging-logkit-impl/" title="avalon-logging-logkit-impl/">avalon-logging-logkit-impl/</a>                                      -         -      
<a href="avalon-logging-logkit-socket/" title="avalon-logging-logkit-socket/">avalon-logging-logkit-socket/</a>                                    -         -      
<a href="avalon-logging-logkit-syslog/" title="avalon-logging-logkit-syslog/">avalon-logging-logkit-syslog/</a>                                    -         -      
<a href="avalon-logging-spi/" title="avalon-logging-spi/">avalon-logging-spi/</a>                                              -         -      
<a href="avalon-logkit-api/" title="avalon-logkit-api/">avalon-logkit-api/</a>                                               -         -      
<a href="avalon-logkit-datagram/" title="avalon-logkit-datagram/">avalon-logkit-datagram/</a>                                          -         -      
<a href="avalon-logkit-impl/" title="avalon-logkit-impl/">avalon-logkit-impl/</a>                                              -         -      
<a href="avalon-logkit-smtp/" title="avalon-logkit-smtp/">avalon-logkit-smtp/</a>                                              -         -      
<a href="avalon-logkit-socket/" title="avalon-logkit-socket/">avalon-logkit-socket/</a>                                            -         -      
<a href="avalon-logkit-syslog/" title="avalon-logkit-syslog/">avalon-logkit-syslog/</a>                                            -         -      
		</pre>
	</main>
	<hr/>
</body>

</html>
"""


def get_dirs(repo_url):
    
    # Extract the versions from the HTML content
    dirs = []
    response = rq.get(repo_url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if '/' in href:
                dirs.append(href)
        # Don't include the ../ dirs[0] (previous directory)
        return dirs[1:]
    return dirs



soup = BeautifulSoup(maven, "html.parser")



for a_tag in soup.find_all("a"):
    print(a_tag)

