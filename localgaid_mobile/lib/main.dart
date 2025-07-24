import 'package:amplify_auth_cognito/amplify_auth_cognito.dart';
import 'package:amplify_flutter/amplify_flutter.dart';
import 'package:amplify_storage_s3/amplify_storage_s3.dart';
import 'package:flutter/material.dart';
import 'package:localgaid_mobile/repositories/place_repository.dart';
import 'package:localgaid_mobile/router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'amplify_outputs.dart';

Future<void> _configureAmplify() async {
  try {
    final auth = AmplifyAuthCognito();
    final storage = AmplifyStorageS3();
    await Amplify.addPlugins([auth, storage]);

    // call Amplify.configure to use the initialized categories in your app
    await Amplify.configure(amplifyConfig);
  } on Exception catch (e) {
    safePrint('An error occurred configuring Amplify: $e');
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _configureAmplify();
  await Supabase.initialize(
    url: 'https://sevbhseieyyrfgaccvjm.supabase.co',
    anonKey:
        'public-api-key',
  );

  final placeRepository = PlaceRepositoryImpl(
    supabaseClient: Supabase.instance.client,
  );

  runApp(LocalGaidApp(placeRepository: placeRepository));
}

class LocalGaidApp extends StatefulWidget {
  final PlaceRepository placeRepository;

  const LocalGaidApp({super.key, required this.placeRepository});

  @override
  State<LocalGaidApp> createState() => _LocalGaidAppState();
}

class _LocalGaidAppState extends State<LocalGaidApp> {
  late AppRouter appRouter;

  @override
  void initState() {
    super.initState();
    appRouter = AppRouter(placeRepository: widget.placeRepository);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      routerDelegate: appRouter.router.routerDelegate,
      routeInformationParser: appRouter.router.routeInformationParser,
      routeInformationProvider: appRouter.router.routeInformationProvider,
    );
  }
}
