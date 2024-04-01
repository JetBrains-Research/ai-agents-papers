import json
import os
import re
from argparse import ArgumentParser
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

LINKS_EMOJIS = {
    "tweet": ":speech_balloon:",
    "code": ":octocat:",
    "website": ":globe_with_meridians:",
    "blogpost": ":writing_hand:",
    "lecture notes": ":writing_hand:",
    "talk": ":mega:",
    "model": ":hugs:",
    "dataset": ":hugs:",
}


TOPICS_EMOJIS = {
    "Agents": ":robot:",
    "Benchmarks & Environments": ":world_map:",
    "Tool Usage": ":wrench:",
    "Reasoning & Planning": ":thinking:",
    "Other": ":bookmark:",
}


def convert_to_markdown_table(df: pd.DataFrame) -> str:
    def _get_date(digest_str: str) -> str:
        matches = re.findall(r"\b(\d{2}\.\d{2}\.\d{4})\b", digest_str)

        date1 = datetime.strftime(datetime.strptime(matches[0], "%d.%m.%Y"), "%B %d")
        date2 = datetime.strftime(datetime.strptime(matches[1], "%d.%m.%Y"), "%B %d")
        return f"{date1} - {date2}"

    def _get_resources_list(df_row: Dict[str, Any]) -> List[str]:
        resources = []

        if df_row["link_tweet"]:
            resources.append(f"[tweet]({df_row['link_tweet']})")

        if df_row["link_code"]:
            resources.append(f"[code]({df_row['link_main']})")

        if df_row["link_website"]:
            resources.append(f"[website]({df_row['link_website']})")

        if df_row["link_other"]:
            for key in df_row["link_other"]:
                resources.append(f"[{key}]({df_row['link_other'][key]})")
        return resources

    def _get_paper(df_row: Dict[str, Any]) -> str:
        paper_title = df_row["title"].replace("\n", " ")
        notes = f" ({df_row['notes']})" if df_row["notes"] else ""

        if df_row["reviews"]:
            title = (
                f"<a href='{df_row['link_main']}'>{paper_title}</a>{notes} – click to unveil highlight by TODO :mag:"
            )
            review = df_row["reviews"].replace("\n", "<br>")
            return f"<details><summary>{title}</summary>{review}</details>"

        return f"[{paper_title}]({df_row['link_main']}){notes}"

    new_df = pd.DataFrame(
        {
            ":scroll: Paper": [_get_paper(row.to_dict()) for _, row in df.iterrows()],
            ":link: Resources": [", ".join(_get_resources_list(row.to_dict())) for _, row in df.iterrows()],
            "Topic": df.topic,
        }
    )

    date = _get_date(df["included_in_digest"].iloc[0])

    result = [f"# Papers we read over {date}"]
    for topic in new_df.Topic.unique():
        result.append(f"## {TOPICS_EMOJIS[topic]} {topic}")
        topic_df = new_df.loc[new_df["Topic"] == topic]
        result.append(topic_df[[":scroll: Paper", ":link: Resources"]].to_markdown(index=False))

    return "\n".join(result)


def convert_to_markdown_list(df: pd.DataFrame) -> str:
    def _process_title(paper_row: pd.DataFrame) -> str:
        title = paper_row["title"].replace("\n", " ")
        title_line = f"[{title}]({paper_row['link_main']})"
        if isinstance(paper_row["notes"], str):
            title_line += f" ({paper_row['notes']})"
        if isinstance(paper_row["hashtags"], str):
            title_line += " " + " ".join([f"`#{hashtag.strip()}`" for hashtag in paper_row["hashtags"].split(",")])
        return title_line

    def _process_links(paper_row: pd.DataFrame) -> List[str]:
        links = []
        for link_type in ["tweet", "code", "website"]:
            if isinstance(paper_row[f"link_{link_type}"], str):
                links.append(f"{LINKS_EMOJIS[link_type]} [{link_type}]({paper_row[f'link_{link_type}']})")
        for link_type in paper_row["link_other"]:
            emoji, _link_type = _process_emojis_in_custom_link(link_type)
            links.append(f"{emoji + ' ' if emoji else ''}[{_link_type}]({paper_row['link_other'][link_type]})")
        return links

    def _process_emojis_in_custom_link(link_type: str) -> Tuple[Optional[str], str]:
        if link_type.startswith(":"):
            return link_type.split(" ")[0], " ".join(link_type.split(" ")[1:])
        return None, link_type

    result = []
    papers = df.loc[df.type == "paper"]
    for topic in papers.topic.unique():
        result.append(f"# {topic}")
        for _, paper_row in papers.loc[papers.topic == topic].sort_values(by="date").iterrows():
            title_line = _process_title(paper_row)
            result.append("* " + title_line)
            links = _process_links(paper_row)
            if links:
                result.append("\t* " + ", ".join(links))
        result.append("")

    not_papers = df.loc[df.type != "paper"]
    if len(not_papers):
        result.append("# Not Papers")
        for _, paper_row in not_papers.sort_values(by=["type", "date"]).iterrows():
            title_line = _process_title(paper_row)
            result.append(f"* {LINKS_EMOJIS.get(paper_row['type'], '')} `#{paper_row['type']}` " + title_line)
            links = _process_links(paper_row)
            if links:
                result.append("\t* " + ", ".join(links))

    return "\n".join(result)


if __name__ == "__main__":
    argparser = ArgumentParser()

    argparser.add_argument(
        "--input-fname",
        type=str,
        help="Name of GSheets-exported file for current digest. Expected to be stored in raw_exports folder.",
    )
    argparser.add_argument(
        "--list",
        action="store_true",
        help="Use to construct a bullet-point style markdown instead of a table.",
    )

    args = argparser.parse_args()

    df = pd.read_csv(os.path.join("../raw_exports", args.input_fname))
    df["type"] = df["type"].str.strip()
    links_list = []
    for link in df.link_other:
        links_list.append(json.loads(link) if isinstance(link, str) else {})
    df["link_other"] = links_list
    df = df.replace({np.nan: None})
    df.to_json(os.path.join("../papers", f"{args.input_fname.split('.csv')[0]}.jsonl"), orient="records", lines=True)

    if args.list:
        md_result = convert_to_markdown_list(df)
    else:
        md_result = convert_to_markdown_table(df)

    with open(os.path.join("../digests", f"{args.input_fname.split('.csv')[0]}.md"), "w") as f:
        f.writelines(md_result)
