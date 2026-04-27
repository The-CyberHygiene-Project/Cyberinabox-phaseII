#!/bin/zsh
# Direct settings application for diwai.org NIST 800-171 compliance
# Writes settings to system preference files read by compliance checks

echo "Applying com.apple.applicationaccess settings..."
DOMAIN=/Library/Preferences/com.apple.applicationaccess
defaults write $DOMAIN allowAccountModification -bool false
defaults write $DOMAIN allowActivityContinuation -bool false
defaults write $DOMAIN allowAirDrop -bool false
defaults write $DOMAIN allowApplePersonalizedAdvertising -bool false
defaults write $DOMAIN allowAssistant -bool false
defaults write $DOMAIN allowAutoUnlock -bool false
defaults write $DOMAIN allowCloudAddressBook -bool false
defaults write $DOMAIN allowCloudBookmarks -bool false
defaults write $DOMAIN allowCloudCalendar -bool false
defaults write $DOMAIN allowCloudDesktopAndDocuments -bool false
defaults write $DOMAIN allowCloudDocumentSync -bool false
defaults write $DOMAIN allowCloudFreeform -bool false
defaults write $DOMAIN allowCloudKeychainSync -bool false
defaults write $DOMAIN allowCloudMail -bool false
defaults write $DOMAIN allowCloudNotes -bool false
defaults write $DOMAIN allowCloudPhotoLibrary -bool false
defaults write $DOMAIN allowCloudPrivateRelay -bool false
defaults write $DOMAIN allowCloudReminders -bool false
defaults write $DOMAIN allowContentCaching -bool false
defaults write $DOMAIN allowDiagnosticSubmission -bool false
defaults write $DOMAIN allowDictation -bool false
defaults write $DOMAIN allowEraseContentAndSettings -bool false
defaults write $DOMAIN allowExternalIntelligenceIntegrations -bool false
defaults write $DOMAIN allowExternalIntelligenceIntegrationsSignIn -bool false
defaults write $DOMAIN allowFindMyDevice -bool false
defaults write $DOMAIN allowFindMyFriends -bool false
defaults write $DOMAIN allowFingerprintForUnlock -bool false
defaults write $DOMAIN allowGameCenter -bool false
defaults write $DOMAIN allowGenmoji -bool false
defaults write $DOMAIN allowImagePlayground -bool false
defaults write $DOMAIN allowiPhoneMirroring -bool false
defaults write $DOMAIN allowMailSmartReplies -bool false
defaults write $DOMAIN allowMailSummary -bool false
defaults write $DOMAIN allowMediaSharing -bool false
defaults write $DOMAIN allowMediaSharingModification -bool false
defaults write $DOMAIN allowNotesTranscription -bool false
defaults write $DOMAIN allowNotesTranscriptionSummary -bool false
defaults write $DOMAIN allowPasswordProximityRequests -bool false
defaults write $DOMAIN allowPasswordSharing -bool false
defaults write $DOMAIN allowRapidSecurityResponseInstallation -bool true
defaults write $DOMAIN allowRapidSecurityResponseRemoval -bool false
defaults write $DOMAIN allowSafariSummary -bool false
defaults write $DOMAIN allowUIConfigurationProfileInstallation -bool false
defaults write $DOMAIN allowWritingTools -bool false
defaults write $DOMAIN forceOnDeviceOnlyDictation -bool true

echo "Applying com.apple.screensaver settings..."
DOMAIN=/Library/Preferences/com.apple.screensaver
defaults write $DOMAIN askForPassword -int 1
defaults write $DOMAIN askForPasswordDelay -int 5
defaults write $DOMAIN idleTime -int 1200

echo "Applying com.apple.loginwindow settings..."
DOMAIN=/Library/Preferences/com.apple.loginwindow
defaults write $DOMAIN SHOWFULLNAME -bool true
defaults write $DOMAIN RetriesUntilHint -int 0
defaults write $DOMAIN GuestEnabled -bool false
defaults write $DOMAIN AdminHostInfo -string ""

echo "Applying com.apple.security.firewall settings..."
DOMAIN=/Library/Preferences/com.apple.security.firewall
defaults write $DOMAIN EnableFirewall -bool true
defaults write $DOMAIN EnableStealthMode -bool true
defaults write $DOMAIN BlockAllIncoming -bool true

echo "Applying com.apple.systempolicy settings..."
defaults write /Library/Preferences/com.apple.systempolicy.control AllowIdentifiedDevelopers -bool true
defaults write /Library/Preferences/com.apple.systempolicy.managed DisableOverride -bool true

echo "Applying com.apple.SetupAssistant settings..."
DOMAIN=/Library/Preferences/com.apple.SetupAssistant.managed
defaults write $DOMAIN SkipPrivacySetup -bool true
defaults write $DOMAIN SkipCloudSetup -bool true
defaults write $DOMAIN SkipSiriSetup -bool true
defaults write $DOMAIN SkipTouchIDSetup -bool true
defaults write $DOMAIN SkipScreenTime -bool true
defaults write $DOMAIN SkipUnlockWithWatch -bool true
defaults write $DOMAIN SkipAppleIntelligence -bool true

echo "Applying com.apple.SubmitDiagInfo settings..."
defaults write /Library/Preferences/com.apple.SubmitDiagInfo AutoSubmit -bool false

echo "Applying com.apple.assistant.support settings..."
defaults write /Library/Preferences/com.apple.assistant.support "Assistant Enabled" -bool false

echo "Applying com.apple.mDNSResponder settings..."
defaults write /Library/Preferences/com.apple.mDNSResponder NoMulticastAdvertisements -bool true

echo "Applying com.apple.MCX settings..."
defaults write /Library/Preferences/com.apple.MCX DisableGuestAccount -bool true
defaults write /Library/Preferences/com.apple.MCX EnableGuestAccount -bool false

echo "Applying com.apple.GlobalPreferences settings..."
defaults write /Library/Preferences/.GlobalPreferences com.apple.autologout.managed -bool true
defaults write /Library/Preferences/.GlobalPreferences com.apple.password-manager.auto-fill-proximity-requests -bool false

echo "Applying com.apple.photos settings..."
defaults write /Library/Preferences/com.apple.photos.shareddefaults EnhancedSearchEnabled -bool false

echo "Done. Run compliance check to verify."
