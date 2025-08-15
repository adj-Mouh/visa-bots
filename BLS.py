from playwright.sync_api import sync_playwright, expect, TimeoutError

def run(playwright):
    # Launch Firefox in non-headless mode to see the browser UI
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the target URL
    page.goto("https://algeria.blsspainglobal.com/DZA/Account/LogIn?ReturnUrl=%2FDZA%2Fappointment%2Fnewappointment")

    try:
        # Locate and fill the email input field
        print("Attempting to find the first 'Email' input field...")
        email_input = page.locator("div:has(label:has-text('Email'))").get_by_role('textbox').first
        expect(email_input).to_be_visible(timeout=10000)
        email_input.fill("adj.mohammed.23@gmail.com")
        print("Successfully filled the email field.")

        # --- THE CHANGE IS HERE ---

        # Locate and click the "Verify" button to proceed to the password page
        print("Locating and clicking the 'Verify' button...")
        verify_button = page.get_by_role("button", name="Verify")
        expect(verify_button).to_be_enabled()
        verify_button.click()
        print("Clicked the 'Verify' button.")

        # Wait for the page to redirect and the password fields to be present
        print("Waiting for the password page to load...")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="password-page-loaded.png")
        print("Password page loaded. Screenshot 'password-page-loaded.png' saved.")

        # STRATEGY: Find the SINGLE password input that is VISIBLE.
        # The website creates many decoy password fields that are hidden.
        # The ':visible' pseudo-selector is crucial here.
        print("Attempting to find the one visible password field among decoys...")
        
        # This locator is the key: it combines type and visibility.
        password_input = page.locator('input[type="password"]:visible')
        
        try:
            # First, wait for exactly one such element to appear.
            # This ensures we don't act too early or if the page is broken.
            expect(password_input).to_have_count(1, timeout=15000)
            print("Successfully located exactly one visible password field.")

            # Now that we have the unique visible field, wait for it to be editable.
            # This handles the 'entry-disabled' state.
            expect(password_input).to_be_editable(timeout=10000)
            print("Password field is visible and editable.")

            # --- IMPORTANT: Replace "YOUR_PASSWORD_HERE" with your actual password or OTP ---
            password_input.fill("YOUR_PASSWORD_HERE")
            print("Successfully filled the password field.")
            page.screenshot(path="password-filled.png")
            print("Screenshot 'password-filled.png' saved.")

        except TimeoutError:
            # This block helps debug if the locator strategy fails.
            all_password_fields = page.locator('input[type="password"]').count()
            visible_password_fields = page.locator('input[type="password"]:visible').count()
            print(f"\n--- DEBUGGING ---")
            print(f"ERROR: Timed out waiting for the password field.")
            print(f"Total password fields found in DOM: {all_password_fields}")
            print(f"Visible password fields found: {visible_password_fields}")
            print("The script expected exactly 1 visible field. Please check 'password-page-loaded.png'.")
            print(f"-----------------\n")
            raise # Re-raise the exception to stop the script

        # After filling the password, click the 'Continue' button.
        print("Locating and clicking the 'Continue' button...")
        # Adjust the "name" attribute if the button text is different (e.g., "Login", "Submit").
        continue_button = page.get_by_role("button", name="Continue")
        expect(continue_button).to_be_enabled()
        continue_button.click()
        print("Clicked the 'Continue' button.")
        
        # Wait for the next page to load
        page.wait_for_load_state("networkidle")
        page.screenshot(path="final-page.png")
        print("Screenshot 'final-page.png' saved after clicking continue.")

        # --- END OF CHANGE ---

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="firefox-error.png")
        print("Saved an error screenshot to firefox-error.png")

    print("Script finished. Pausing for 5 seconds before closing...")
    page.wait_for_timeout(5000)
    
    # Cleanly close the browser and context
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
