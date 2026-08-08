from app.services.knowledge import extract_text,score_item

def test_text_upload_extract():
    assert 'hello' in extract_text('x.txt',b'hello world')

def test_relevance():
    assert score_item('cloud migration risk','cloud security migration plan')>=2
