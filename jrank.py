from lxml import html
import requests
import urllib

scimago_home_url = "http://www.scimagojr.com/"
eigenfactor_home_url = "http://eigenfactor.org/projects/journalRank/rankings.php?bsearch="
eigenfactor_home_url_postfix = "&searchby=journal&orderby=eigenfactor"

show_top_results_for_selection = 10

def calculate_fast_ranking(hIndex, sjr, cpd, ef, ai):
    # SJR
    if sjr < 0.06:
        sjr_fast = sjr/0.06*50
    elif sjr < 0.07:
        sjr_fast = 50
    elif sjr < 0.085:
        sjr_fast = 65
    elif sjr < 0.1:
        sjr_fast = 80
    else:
        sjr_fast = 100


    if hIndex < 40:
        hIndex_fast = hIndex/40*50
    elif hIndex < 50:
        hIndex_fast = 50
    elif hIndex < 65:
        hIndex_fast = 65
    elif hIndex < 80:
        hIndex_fast = 80
    else:
        hIndex_fast = 100


    if cpd < 0.5:
        cpd_fast = 0.5/1*50
    elif cpd < 1:
        cpd_fast = 50
    elif cpd < 1.5:
        cpd_fast = 65
    elif cpd < 2:
        cpd_fast = 80
    else:
        cpd_fast = 100


    # Compute aggregates
    total_rank = ai + ef + sjr_fast + hIndex_fast + cpd_fast
    percent_rank = total_rank / 500. * 100. # convert to float

    if percent_rank < 50:
        category = "Quality Compliant"
    elif percent_rank < 60:
        category = "Honorable Mention"
    elif percent_rank < 70:
        category = "Bronze"
    elif percent_rank < 80:
        category = "Silver"
    else:
        category = "Gold"


    # output summaries
    print "\t\t", "Score\tFAST Score"
    print "Article Inf:\t%d\t%d " % (ai, ai)
    print "Eigen Factor:\t%d\t%d " % (ef, ef)
    print "SJR\t\t%.4f\t%d " % (sjr, sjr_fast)
    print "hIndex\t\t%d\t%d " % (hIndex, hIndex_fast)
    print "Cites/Doc\t%.2f\t%d " % (cpd, cpd_fast)
    print "\t\t\t-----"
    print "\t\t\t%d/%d" % (total_rank, 500)
    print "\t\t\t%.2f%%" % (percent_rank)
    print "\t\t\t%s" % (category)

# no user-editable choices beyond this point
# ==========================================

def search_for_journal(target_journal_name, scimago_home_url):

    search_url = scimago_home_url + "journalsearch.php?q=" + target_journal_name

    page = requests.get(search_url)
    print page
    tree = html.fromstring(page.content)

    journal_list = tree.xpath('//a[span[@class="jrnlname"]]')

    filtered_journal_list = []
    for journal_link in journal_list:
        href = journal_link.attrib['href']
        name = journal_link.xpath('./span/text()')
        filtered_journal_list.append((href, name[0]))
        # print html.tostring(journal_link)

    return filtered_journal_list

def ask_user_for_choice(filtered_journal_list, show_top_results_for_selection):

    if len(filtered_journal_list) < 1:
        print "---------------------------------------------------------------------"
        print "--- Failed to find journal in Scimago. Results will be wrong."
        print "---------------------------------------------------------------------"
        return ""

    i = 1
    print "Please pick from the following to get ranking: "
    for record in filtered_journal_list:
        print i, "-", record[1]
        i += 1
        if i > show_top_results_for_selection: break

    try:
        # todo: change later
        choice = int(raw_input("Enter choice: "))
        if choice < 1 or choice > (show_top_results_for_selection):
            raise ValueError

    except ValueError:
        print "Please pick between 1 and", min(show_top_results_for_selection, i)
        import sys
        sys.exit(1)

    selected_journal = filtered_journal_list[choice - 1] # zero-based index
    return selected_journal



# ------ choice made. Now get the metrics and calcuate
def get_journal_metrics_from_scimago(scimago_home_url, chosen_journal):
    journal_url = scimago_home_url + chosen_journal[0]
    page = requests.get(journal_url)
    tree = html.fromstring(page.content)
    # print html.tostring(tree)
    title = tree.xpath('//title')[0].text
    # print "Displaying results for: ", title
    hIndex= int(tree.xpath('//div[@class="hindexnumber"]/text()')[0])
    # print hIndex

    sjr_th = tree.xpath("//th[text() = 'SJR']")[0]
    sjr_table = sjr_th.getparent().getparent().getparent()
    # get the last td since that is the latest SJR
    sjr = float(sjr_table.xpath('.//td/text()')[-1])

    cpd_th = tree.xpath("//th[text() = 'Cites per document']")[0]
    cpd_table = cpd_th.getparent().getparent().getparent()
    # get the last td since that is the latest CPD
    cpd = float(cpd_table.xpath('.//td/text()')[-1])
    return (title, hIndex, sjr, cpd)


# need to get Eigen Factor values separately
def get_journal_metrics_from_eigenfactor(eigenfactor_home_url, target_journal_name, eigenfactor_home_url_postfix):
    ef_url = eigenfactor_home_url + target_journal_name + eigenfactor_home_url_postfix
    # print ef_url
    page = requests.get(ef_url)
    # print page.content
    tree = html.fromstring(page.content)
    try:
        title = tree.xpath('//div[@class="journal"]/text()')[0]
        # looks like we use percentiles and not the actual values so use pnum* instead of AI and EF
        eigen_factor = int(tree.xpath('//div[@class="pnum1"]/text()')[0])
        article_influence = int(tree.xpath('//div[@class="pnum2"]/text()')[0])
    except IndexError:
        print "---------------------------------------------------------------------"
        print "--- Failed to find journal in EigenFactor.org. Results will be wrong."
        print "---------------------------------------------------------------------"
        title = "Not found."
        eigen_factor = 0
        article_influence = 0

    return title, eigen_factor, article_influence

# main control
if __name__ == "__main__":
    target_journal_name = raw_input("Please enter journal name: ")

    filtered_journal_list = search_for_journal(target_journal_name, scimago_home_url)
    chosen_journal = ask_user_for_choice(filtered_journal_list, show_top_results_for_selection)
    if chosen_journal == "":
        print "No journal selected. Aborting."
        import sys
        sys.exit(1)

    scimago_title, hIndex, sjr, cpd = get_journal_metrics_from_scimago(scimago_home_url, chosen_journal)

    ef_title, eigen_factor, article_influence = get_journal_metrics_from_eigenfactor(eigenfactor_home_url, target_journal_name, eigenfactor_home_url_postfix)

    print "Details found. Please verify titles before using the metrics."
    print "- Scimago Title:     ", scimago_title
    # print "- hIndex:            ", hIndex
    # print "- SJR:               ", sjr
    # print "- Cites per doc:     ", cpd
    print "- Eigenfactor Title: ", ef_title
    # print "- Eigenfactor:       ", eigen_factor
    # print "- Article Influence: ", article_influence
    print ' '

    calculate_fast_ranking(hIndex, sjr, cpd, eigen_factor, article_influence)
