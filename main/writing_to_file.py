### Writing the extracted links to a file
import tldextract
import pdb

def write_to_file(key,links):
    flag = True
    temp = []
    with open('advancedurls.txt','a') as f:
        f.write("Keyword:"+key)
        f.write("Total number of links extracted:"+str(len(links)))
        f.write("\n\n")
        for link in links:
            #pdb.set_trace()
            check_link = tldextract.extract(link).domain
            if flag is True:
                f.write(str(link)+"\n")  
                temp.append(check_link) 
                flag = False
            elif check_link not in temp: ##checking for duplicate url with the host name
                f.write(str(link))  
                temp.append(check_link)
            else:
                print "Already available: ",check_link
                continue
        f.write("\n")
