<?php
/**
 * Install Omeka S, its modules, and an API key, from the command line.
 *
 * The three things Omeka's REST API cannot do for itself: the first-run
 * installer is a web form, modules are only installed from the admin
 * interface, and so are API keys. This does all three through Omeka's own
 * services, the same calls the installer form and the admin pages make, so
 * everything after it can go through the public API.
 *
 * Prerequisites: run inside the omeka container as www-data, with the
 * database up and OMEKA_ADMIN_NAME, OMEKA_ADMIN_EMAIL and OMEKA_ADMIN_PASSWORD
 * set (compose.yaml passes them through from .env).
 *
 * Usage, normally via scripts/install.sh:
 *   php /opt/tetrak-omeka/setup.php install   # no-op if already installed
 *   php /opt/tetrak-omeka/setup.php modules   # installs and activates MODULES
 *   php /opt/tetrak-omeka/setup.php api-key   # prints "<identity> <credential>"
 *
 * They are separate commands, run as separate processes, because Omeka
 * decides at start-up whether it is installed and builds its permissions from
 * that: everything is allowed until it is installed.
 *
 * api-key replaces any key it issued earlier for the same user, since Omeka
 * stores only a hash and an old credential cannot be shown again.
 */

require '/var/www/html/bootstrap.php';

const KEY_LABEL = 'tetrak-omeka scripts';

// Modules the demo needs; their files are put in place by omeka/Dockerfile.
const MODULES = ['OctopusViewer'];

function fail(string $message): void
{
    fwrite(STDERR, "setup.php: $message\n");
    exit(1);
}

function env(string $name): string
{
    $value = getenv($name);
    if ($value === false || $value === '') {
        fail("$name is not set -- add it to .env (see .env.example)");
    }
    return $value;
}

$command = $argv[1] ?? '';
if (!in_array($command, ['install', 'modules', 'api-key'], true)) {
    fail('usage: setup.php install|modules|api-key');
}

$application = Omeka\Mvc\Application::init(
    require OMEKA_PATH . '/application/config/application.config.php'
);
$services = $application->getServiceManager();
$installed = $services->get('Omeka\Status')->isInstalled();

if ($command === 'install') {
    if ($installed) {
        fwrite(STDERR, "Omeka is already installed\n");
        exit(0);
    }

    $email = env('OMEKA_ADMIN_EMAIL');
    $installer = $services->get('Omeka\Installer');
    $installer->registerVars('Omeka\Installation\Task\CreateFirstUserTask', [
        'name' => env('OMEKA_ADMIN_NAME'),
        'email' => $email,
        'password-confirm' => ['password' => env('OMEKA_ADMIN_PASSWORD')],
    ]);
    $installer->registerVars('Omeka\Installation\Task\AddDefaultSettingsTask', [
        'administrator_email' => $email,
        'installation_title' => getenv('OMEKA_TITLE') ?: 'Tetrak and Omeka demo',
        'time_zone' => 'UTC',
        'locale' => '',
    ]);

    if (!$installer->install()) {
        fail('installation failed: ' . json_encode($installer->getErrors()));
    }
    fwrite(STDERR, "Omeka installed; admin is $email\n");
    exit(0);
}

if (!$installed) {
    fail('Omeka is not installed yet -- run "setup.php install" first');
}

$email = env('OMEKA_ADMIN_EMAIL');
$entityManager = $services->get('Omeka\EntityManager');
$user = $entityManager->getRepository(Omeka\Entity\User::class)
    ->findOneBy(['email' => $email]);
if (!$user) {
    fail("no user with the email $email -- set OMEKA_ADMIN_EMAIL to an existing admin");
}

if ($command === 'modules') {
    // Installing a module is checked against the current user's permissions,
    // so act as the admin, as Omeka's own background jobs act as their owner.
    $services->get('Omeka\AuthenticationService')->getStorage()->write($user);
    $manager = $services->get('Omeka\ModuleManager');
    foreach (MODULES as $id) {
        $module = $manager->getModule($id);
        $state = $module ? $module->getState() : 'not_found';
        if ($state === Omeka\Module\Manager::STATE_NOT_INSTALLED) {
            $manager->install($module);
            fwrite(STDERR, "Module $id installed\n");
        } elseif ($state === Omeka\Module\Manager::STATE_NOT_ACTIVE) {
            $manager->activate($module);
            fwrite(STDERR, "Module $id activated\n");
        } elseif ($state !== Omeka\Module\Manager::STATE_ACTIVE) {
            fail("module $id cannot be installed: its state is \"$state\"");
        }
    }
    exit(0);
}

// api-key

$keys = $user->getKeys();
foreach ($keys as $id => $key) {
    if ($key->getLabel() === KEY_LABEL) {
        $keys->remove($id);
    }
}

$key = new Omeka\Entity\ApiKey;
$key->setId();
$key->setLabel(KEY_LABEL);
$key->setOwner($user);
$credential = $key->setCredential();
$entityManager->persist($key);
$entityManager->flush();

echo $key->getId(), ' ', $credential, "\n";
