"""Declared local web resources must exist; source checks do not prove rendering."""
import json
import unittest
from unittest.mock import patch

from brain_programming import candidate_contract_gate, programming_intent
from project_archive import project_markdown
from web_module_contract import module_dependency_gaps


def files(html, others=(), entry='index.html'):
    return [{'path':entry,'language':'html','content':html},
            *[{'path':path,'language':'css' if path.endswith('.css') else 'text','content':content}
              for path,content in others]]


def gaps(html, others=(), entry='index.html'):
    return module_dependency_gaps(html,files(html,others,entry))


class WebAssetContract(unittest.TestCase):
    def test_missing_stylesheet_image_and_icon_are_reported(self):
        html='<link rel="stylesheet" href="styles.css"><img src="assets/hero.svg"><link rel="shortcut icon" href="icon.svg">'
        self.assertCountEqual(gaps(html),[
            'missing-project-asset:styles.css','missing-project-asset:assets/hero.svg',
            'missing-project-asset:icon.svg'])

    def test_complete_local_files_resolve_from_nested_html_with_query_and_hash(self):
        html='<link rel="stylesheet" href="../css/theme.css?v=2"><img src="../assets/hero.svg#part">'
        self.assertEqual(gaps(html,[('css/theme.css','body {color:green}'),
                                   ('assets/hero.svg','<svg></svg>')],'pages/index.html'),[])

    def test_classic_script_file_is_required_but_non_executable_script_data_is_not(self):
        html='<script src="src/app.js"></script><script type="application/json" src="data.json"></script>'
        self.assertEqual(gaps(html),['missing-project-asset:src/app.js'])
        self.assertEqual(gaps(html,[('src/app.js','const value=1;')]),[])

    def test_percent_encoded_dot_segments_resolve_without_inventing_a_missing_asset(self):
        html='<link rel="stylesheet" href="css/main.css">'
        others=[('css/main.css','body{background:url(%2e%2e/assets/bg.svg)}'),
                ('assets/bg.svg','<svg></svg>')]
        self.assertEqual(gaps(html,others),[])

    def test_css_urls_use_stylesheet_parent_and_preserve_encoded_spaces(self):
        html='<link rel="stylesheet" href="css/theme.css">'
        others=[('css/theme.css','body {background:url("../assets/hero%20image.svg?v=1#shape")}'),
                ('assets/hero image.svg','<svg></svg>')]
        self.assertEqual(gaps(html,others),[])
        self.assertEqual(gaps(html,others[:1]),['missing-project-asset:assets/hero image.svg'])

    def test_imported_css_follows_own_parent_and_reports_transitive_missing_file(self):
        html='<link rel="stylesheet" href="css/main.css">'
        others=[('css/main.css','@import "themes/dark.css" screen;'),
                ('css/themes/dark.css','@import url("../base.css"); body{background:url(../../assets/bg.svg)}'),
                ('css/base.css','body{color:white}')]
        self.assertEqual(gaps(html,others),['missing-project-asset:assets/bg.svg'])
        self.assertEqual(gaps(html,others+[('assets/bg.svg','<svg></svg>')]),[])

    def test_import_cycle_and_shared_stylesheet_are_traversed_once(self):
        html='<link rel="stylesheet" href="a.css"><link rel="stylesheet" href="a.css">'
        project=files(html,[('a.css','@import "b.css";'),('b.css','@import "a.css";')])
        project.append({'path':'second.html','language':'html','content':html})
        from web_module_contract import _css_references
        with patch('web_module_contract._css_references',wraps=_css_references) as inspect:
            self.assertEqual(module_dependency_gaps(html,project),[])
        self.assertEqual(inspect.call_count,2)

    def test_inline_styles_and_style_attributes_are_checked(self):
        html='<style>.hero{background:url(images/bg.svg)}</style><div style="mask-image:url(icons/clip.svg)"></div>'
        self.assertCountEqual(gaps(html),['missing-project-asset:images/bg.svg','missing-project-asset:icons/clip.svg'])

    def test_base_element_changes_html_and_inline_style_reference_parent(self):
        html='<base href="../assets/"><img src="hero.svg"><style>body{background:url(bg.svg)}</style>'
        self.assertCountEqual(gaps(html,entry='pages/index.html'),[
            'missing-project-asset:assets/hero.svg','missing-project-asset:assets/bg.svg'])
        self.assertEqual(gaps(html,[('assets/hero.svg','<svg></svg>'),('assets/bg.svg','<svg></svg>')],
                              'pages/index.html'),[])

    def test_first_empty_base_href_still_blocks_later_base_override(self):
        html='<base href=""><base href="elsewhere/"><img src="hero.svg">'
        self.assertEqual(gaps(html,[('hero.svg','<svg></svg>')]),[])

    def test_external_base_and_resource_schemes_are_never_fetched_or_invented_missing(self):
        html='<base href="https://example.invalid/assets/"><img src="hero.svg"><link rel="stylesheet" href="theme.css">'
        self.assertEqual(gaps(html),[])
        html='<img src="https://example.invalid/image.png"><img src="//example.invalid/a.svg"><img src="data:image/svg+xml,<svg/>"><img src="blob:opaque"><style>body{background:url(#local-mask);src:url(data:font/woff2;base64,AAAA)}</style>'
        self.assertEqual(gaps(html),[])

    def test_comments_and_css_content_strings_do_not_declare_resources(self):
        html='<style>/* url(missing.svg) @import "missing.css"; */ body::before { content: "url(missing.png)"; custom:myurl(missing.svg) }</style>'
        self.assertEqual(gaps(html),[])

    def test_unterminated_css_comment_and_string_never_expose_embedded_urls(self):
        for content in ('/* '+'/* url(missing.svg) '*10000,
                        'body::before{content:"'+'\\"url(missing.svg)'*10000+'\\'):
            self.assertEqual(gaps('<style>'+content+'</style>'),[])

    def test_unrelated_css_is_not_scanned(self):
        self.assertEqual(gaps('<h1>Starter</h1>',[('unused.css','body{background:url(missing.svg)}')]),[])

    def test_css_escaped_and_dynamic_urls_are_explicitly_ungraded(self):
        html='<style>body{background:url(var(--asset));mask:url("escaped\\ name.svg")}</style>'
        self.assertEqual(gaps(html),[])

    def test_srcset_and_navigation_links_are_explicitly_ungraded(self):
        html='<img srcset="small.svg 1x, large.svg 2x"><a href="route">Go</a><link rel="canonical" href="page">'
        self.assertEqual(gaps(html),[])

    def test_supported_build_required_project_keeps_existing_separate_verification(self):
        package=json.dumps({'devDependencies':{'vite':'5.4.0'},'scripts':{'dev':'vite'}})
        html='<link rel="stylesheet" href="/src/theme.css"><img src="/generated/image.svg">'
        self.assertEqual(gaps(html,[('package.json',package)]),[])
        fake=json.dumps({'scripts':{'dev':'echo vite'}})
        self.assertCountEqual(gaps(html,[('package.json',fake)]),[
            'missing-project-asset:src/theme.css','missing-project-asset:generated/image.svg'])

    def test_real_shared_contract_rejects_missing_asset_without_execution_claim(self):
        html='<!doctype html><html><head><link rel="stylesheet" href="styles.css"></head><body><h1>Tasks</h1><img src="hero.svg"></body></html>'
        intent=programming_intent('Build an HTML starter project for a task tracker.',[],[])
        result=candidate_contract_gate(project_markdown(files(html)),intent,[])
        self.assertEqual(result['status'],'REJECT',result)
        self.assertIn('missing-project-asset:styles.css',result['reasons'])
        self.assertIn('missing-project-asset:hero.svg',result['reasons'])
        self.assertFalse(result['executionVerified'])

    def test_invalid_external_url_does_not_raise_during_source_validation(self):
        self.assertEqual(gaps('<img src="https://[broken.invalid/a.svg">'),[])

    def test_invalid_document_base_is_actionable_rejection_not_a_validator_crash(self):
        self.assertEqual(gaps('<base href="https://["><img src="hero.svg">'),
                         ['invalid-project-asset-base'])

    def test_media_svg_and_image_input_references(self):
        html='<video src="clip.mp4" poster="poster.svg"></video><source src="audio.ogg"><input type="image" src="send.svg"><svg><image href="layer.svg"/></svg>'
        self.assertCountEqual(gaps(html),['missing-project-asset:'+name for name in
                                        ['clip.mp4','poster.svg','audio.ogg','send.svg','layer.svg']])


if __name__=='__main__':unittest.main()
