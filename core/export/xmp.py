from pathlib import Path
import xml.etree.ElementTree as ET


def write_xmp_sidecar(image_path: str, rating: int = 0,
                       label: str = "", tags: list[str] | None = None) -> str:
    xmp_path = Path(image_path).with_suffix(".xmp")
    tags = tags or []
    rating = max(0, min(5, rating))
    subjects = "".join(f"      <rdf:li>{t}</rdf:li>\n" for t in tags)
    xmp_content = f"""<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='PhotoStudioHub 1.0'>
  <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
    <rdf:Description rdf:about=''
      xmlns:xmp='http://ns.adobe.com/xap/1.0/'
      xmlns:dc='http://purl.org/dc/elements/1.1/'
      xmlns:lr='http://ns.adobe.com/lightroom/1.0/'>
      <xmp:Rating>{rating}</xmp:Rating>
      <xmp:Label>{label}</xmp:Label>
      <dc:subject>
        <rdf:Bag>
{subjects}        </rdf:Bag>
      </dc:subject>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'?>"""
    xmp_path.write_text(xmp_content, encoding="utf-8")
    return str(xmp_path)


def write_xmp_from_cull_result(cull_result: dict) -> list[str]:
    written = []
    for r in cull_result.get("selects", []):
        path = r["path"]
        score = r.get("score", 0)
        rating = min(5, max(1, int(score / 20)))
        tags = ["PSH_select"]
        if r.get("expression", {}) and r["expression"].get("faces"):
            emo = r["expression"]["faces"][0].get("dominant_emotion", "")
            if emo:
                tags.append(f"emotion_{emo}")
        xmp = write_xmp_sidecar(path, rating=rating, label="Green", tags=tags)
        written.append(xmp)
    for r in cull_result.get("rejects", []):
        xmp = write_xmp_sidecar(r["path"], rating=1, label="Red", tags=["PSH_reject"])
        written.append(xmp)
    return written
