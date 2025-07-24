import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:localgaid_mobile/repositories/place_repository.dart';
import 'package:localgaid_mobile/screens/place_detail_screen.dart';
import 'package:localgaid_mobile/screens/places_screen.dart';

final RouteObserver<ModalRoute> routeObserver = RouteObserver<ModalRoute>();

class AppRouter {
  final PlaceRepository placeRepository;

  AppRouter({required this.placeRepository});

  late final router = GoRouter(
    observers: [routeObserver],
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (BuildContext context, GoRouterState state) {
          return PlacesScreen(placeRepository: placeRepository);
        },
        routes: <RouteBase>[
          GoRoute(
            path: 'places/:placeId',
            builder: (BuildContext context, GoRouterState state) {
              return PlaceDetailScreen(
                placeRepository: placeRepository,
                placeId: int.parse(state.pathParameters['placeId']!),
              );
            },
          ),
        ],
      ),
    ],
  );
}
