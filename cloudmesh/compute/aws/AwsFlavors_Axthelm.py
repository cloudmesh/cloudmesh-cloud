import urllib.request
import contextlib
import re

def gather_aws_ec2_instance_types(
        instance_type_url="https://aws.amazon.com/ec2/instance-types/"
):

    with contextlib.closing(urllib.request.urlopen(instance_type_url)) as x:
        raw_html = x.read().decode("utf8")
    # remove formatting html
    raw_html = re.sub(pattern = "<b>|</b>|<br />", repl = "", string = raw_html)

    # search for tables
    tables = re.findall(pattern = "<table.*?</table>", string = raw_html, flags=re.DOTALL)

    output = []
    for t in tables:
        # check that headers exists
        model_header = (re.search("Model", t) is not None)
        vcpu_header = (re.search("vCPU", t) is not None)
        mem_header = (re.search("Mem(ory)* \([GT]iB\)", t) is not None)
        if (model_header and vcpu_header and mem_header):
            rows = re.findall(pattern = "<tr>.*?</tr>", string = t, flags=re.DOTALL)
            for idx_r, row in enumerate(rows):
                cols = re.findall(pattern = "<td.*?>(.*?)</td>", string = row, flags=re.DOTALL)
                if idx_r == 0 :
                    headers = cols
                else:
                    output.append(dict(zip(headers, cols)))
    return output

def gather_aws_ec2_prices(
        region="reg-us-east",
        pricing_url = "https://aws.amazon.com/ec2/spot/pricing/"
):

    with contextlib.closing(urllib.request.urlopen(pricing_url)) as x:
        raw_html = x.read().decode("utf8")
    # remove formatting html
    raw_html = re.sub(pattern = "<b>|</b>", repl = "", string = raw_html)

