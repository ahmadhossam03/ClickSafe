def url_behavior_classification(url, output):
    feature_values = {}
    flags = []

    weights = {
        "redirect_status": 1.2,
        "meta_refresh": 1.2,
        "js_redirect": 1.2,
        "insecure_form": 1.1,
        "hidden_elements": 1.1
    }

    try:
        output.append("\n[🔎] URL Behavior Analysis")

        # 3. Redirect status
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        if 300 <= resp.status_code < 400:
            feature_values["redirect_status"] = 5
            flags.append(f"Redirect status code {resp.status_code}")
        else:
            feature_values["redirect_status"] = 1

        # 4. Meta refresh
        meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta and 'url=' in meta.get('content', '').lower():
            feature_values["meta_refresh"] = 5
            flags.append("Meta refresh redirection")
        else:
            feature_values["meta_refresh"] = 1

        # 5. JS redirection
        js_redirect_keywords = ['window.location', 'location.replace', 'location.assign']
        js_found = False
        for script in soup.find_all('script'):
            if script.string and any(kw in script.string for kw in js_redirect_keywords):
                js_found = True
                break
        if js_found:
            feature_values["js_redirect"] = 5
            flags.append("JS redirection script found")
        else:
            feature_values["js_redirect"] = 1

        # 6. Insecure form actions
        insecure_found = False
        for form in soup.find_all('form'):
            if form.get('action', '').startswith('http://'):
                insecure_found = True
                break
        if insecure_found:
            feature_values["insecure_form"] = 5
            flags.append("Form uses insecure HTTP action")
        else:
            feature_values["insecure_form"] = 1

        # 7. Hidden elements
        hidden_elements = soup.select('[style*="display:none"], [style*="visibility:hidden"]')
        if hidden_elements:
            feature_values["hidden_elements"] = 5
            flags.append("Hidden HTML elements detected")
        else:
            feature_values["hidden_elements"] = 1

        # Apply weights and calculate weighted average
        weighted_sum = 0
        total_weight = 0
        for feature, value in feature_values.items():
            weight = weights.get(feature, 1.0)
            weighted_sum += value * weight
            total_weight += weight

        final_score = weighted_sum / total_weight if total_weight > 0 else 1.0
        final_score = round(final_score, 2)

        # Output details
        for flag in flags:
            output.append(f" - {flag}")
        output.append(f"\nURL Behavior Score: {final_score:.2f}")

        return final_score

    except Exception as e:
        output.append(f"Error in behavior analysis: {e}")
        return 1.0  # fallback score on error
